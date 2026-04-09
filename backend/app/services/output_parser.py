"""解析 Agent 输出 — 方案B：JSON 格式解析"""
import json
import re
from typing import Any

from app.models.schemas import AuditRecord


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

        risk_level_raw = str(item.get("risk_level", "needs_manual_review"))
        risk_level = _normalize_risk_level(risk_level_raw)

        risk_description = str(item.get("risk_description", ""))
        suggestion = str(item.get("suggestion", ""))

        refs = _extract_refs(risk_description)

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
            )
        )

    return records
