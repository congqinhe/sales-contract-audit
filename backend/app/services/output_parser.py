"""解析 Agent 输出 — 方案B：JSON 格式解析"""
import json
import logging
import re
from typing import Any, Optional

from app.models.schemas import AuditRecord

logger = logging.getLogger(__name__)


def _parse_span_int(val: Any) -> Optional[int]:
    if val == "未找到" or val is None:
        return None
    if isinstance(val, bool):
        return None
    if isinstance(val, int):
        return val if val >= 0 else None
    try:
        n = int(str(val).strip())
        return n if n >= 0 else None
    except ValueError:
        return None


def _normalize_evidence_spans(raw: Any) -> list[dict[str, Any]]:
    """解析 LLM 输出的 evidence_spans，统一为 paragraph_start/end (+可选 brief)。"""
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for el in raw:
        if not isinstance(el, dict):
            continue
        ps = _parse_span_int(el.get("paragraph_start", el.get("start")))
        pe = _parse_span_int(el.get("paragraph_end", el.get("end")))
        if ps is None or pe is None:
            continue
        if pe < ps:
            ps, pe = pe, ps
        key = (ps, pe)
        if key in seen:
            continue
        seen.add(key)
        brief = str(el.get("brief", el.get("note", ""))).strip()
        item: dict[str, Any] = {"paragraph_start": ps, "paragraph_end": pe}
        if brief:
            item["brief"] = brief
        out.append(item)
    return out


def _refs_from_evidence_spans(spans: list[dict[str, Any]]) -> list[dict]:
    refs: list[dict] = []
    for s in spans:
        ps = s.get("paragraph_start")
        pe = s.get("paragraph_end")
        if isinstance(ps, int) and isinstance(pe, int):
            refs.append({"start": ps, "end": pe})
    return refs


def _merge_ref_dicts(*ref_lists: list[dict]) -> list[dict]:
    seen: set[tuple[int, int]] = set()
    merged: list[dict] = []
    for lst in ref_lists:
        for r in lst:
            start = r.get("start")
            end = r.get("end")
            if not isinstance(start, int) or not isinstance(end, int):
                continue
            key = (start, end)
            if key in seen:
                continue
            seen.add(key)
            merged.append({"start": start, "end": end})
    return merged


def _extract_refs(text: str) -> list[dict]:
    """从文本中提取 {{id:X-Y}} 或 {{id:X}} 段落引用"""
    refs = []
    for m in re.finditer(r"\{\{id:(\d+)(?:-(\d+))?\}\}", text):
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        refs.append({"start": start, "end": end})
    return refs


def _normalize_risk_level(raw: str) -> str:
    """将 LLM 可能输出的各种风险等级表述规范化"""
    r = raw.strip().lower()
    if r in ("risk", "有风险", "存在风险", "高风险", "重大风险"):
        return "risk"
    if r in ("no_risk", "无风险", "已规避", "低风险", "风险较低"):
        return "no_risk"
    if r in ("needs_manual_review", "需人工核验", "待确认", "需确认"):
        return "needs_manual_review"
    if r in ("not_applicable", "不适用"):
        return "not_applicable"
    if "风险" in r and ("无" in r or "低" in r or "规避" in r):
        return "no_risk"
    if "风险" in r:
        return "risk"
    if "人工" in r or "核验" in r or "确认" in r:
        return "needs_manual_review"
    return "risk"


def _strip_json_fences(raw: str) -> str:
    """移除 LLM 输出中可能包裹的 markdown 代码块标记"""
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def _repair_truncated_json(text: str) -> list[dict[str, Any]]:
    """尝试修复被截断的 JSON 数组，抢救已完成的对象。

    策略：从末尾向前找到最后一个完整的 '}' 对象边界，
    截断后补上 ']' 再解析。
    """
    start = text.find("[")
    if start == -1:
        return []

    fragment = text[start:]
    last_brace = fragment.rfind("}")
    if last_brace == -1:
        return []

    candidate = fragment[: last_brace + 1].rstrip().rstrip(",") + "]"
    try:
        data = json.loads(candidate)
        if isinstance(data, list):
            logger.info("截断 JSON 修复成功，抢救出 %d 条记录", len(data))
            return data
    except json.JSONDecodeError:
        pass
    return []


def _safe_parse_json(raw: str) -> list[dict[str, Any]]:
    """尝试从 LLM 输出中解析 JSON 数组，带容错"""
    text = _strip_json_fences(raw)

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    bracket_match = re.search(r"\[.*\]", text, re.DOTALL)
    if bracket_match:
        try:
            data = json.loads(bracket_match.group())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    repaired = _repair_truncated_json(text)
    if repaired:
        return repaired

    if text:
        logger.warning("JSON 解析完全失败, raw_len=%d, head=%.200s", len(text), text[:200])
    return []


def parse_module_output(raw: str, module: str = "") -> list[AuditRecord]:
    """
    解析模块级 Agent 输出（JSON 数组格式），返回 AuditRecord 列表。
    """
    items = _safe_parse_json(raw)
    records: list[AuditRecord] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        rule_id = str(item.get("rule_id", ""))
        review_point = str(item.get("review_point", ""))
        review_type = str(item.get("review_type", "judge"))

        para_start = item.get("paragraph_start", "未找到")
        para_end = item.get("paragraph_end", "未找到")

        if isinstance(para_start, str) and para_start not in ("未找到",):
            try:
                para_start = int(para_start)
            except ValueError:
                para_start = "未找到"
        if isinstance(para_end, str) and para_end not in ("未找到",):
            try:
                para_end = int(para_end)
            except ValueError:
                para_end = "未找到"

        contract_quote = str(item.get("contract_quote", "未找到相关条款"))
        extracted_info = item.get("extracted_info", {})
        if not isinstance(extracted_info, dict):
            extracted_info = {}
        extracted_info.pop("evidence_spans", None)

        risk_level_raw = str(item.get("risk_level", "needs_manual_review"))
        risk_level = _normalize_risk_level(risk_level_raw)

        risk_description = str(item.get("risk_description", ""))
        suggestion = str(item.get("suggestion", ""))

        evidence_spans = _normalize_evidence_spans(item.get("evidence_spans"))
        span_refs = _refs_from_evidence_spans(evidence_spans)
        refs = _merge_ref_dicts(_extract_refs(risk_description), span_refs)

        records.append(
            AuditRecord(
                rule_id=rule_id,
                module=module,
                review_point=review_point,
                review_type=review_type,
                paragraph_start=para_start,
                paragraph_end=para_end,
                contract_quote=contract_quote,
                extracted_info=extracted_info,
                risk_level=risk_level,
                risk_description=risk_description,
                suggestion=suggestion,
                refs=refs,
                evidence_spans=evidence_spans,
            )
        )

    return records
