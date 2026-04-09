"""解析 Agent 输出格式：风险要素|段落编号起始|段落编号结尾|原文文本|风险判断结论及原因"""
import re
from typing import Optional

from app.models.schemas import AuditRecord


def _extract_refs(text: str) -> list[dict]:
    """从结论文本中提取 {{id:X-Y}} 或 {{id:X}} 引用"""
    refs = []
    # 匹配 {{id:46-51}} 或 {{id:46}}
    for m in re.finditer(r"\{\{id:(\d+)(?:-(\d+))?\}\}", text):
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        refs.append({"start": start, "end": end})
    return refs


def _infer_risk_level(conclusion: str) -> str:
    """从结论文本推断风险等级"""
    c = conclusion.lower()
    if "无风险" in c or "风险较低" in c or "已规避" in c or "无此项约定" in c:
        return "低风险"
    if "高风险" in c or "存在重大风险" in c:
        return "高风险"
    return "中风险"


def _is_valid_para_id(s: str) -> bool:
    """段落编号是否为有效格式：纯数字或"未找到" """
    if s == "未找到":
        return True
    try:
        n = int(s)
        return n >= 1
    except (ValueError, TypeError):
        return False


def parse_agent_output(raw: str) -> list[AuditRecord]:
    """
    解析 Agent 输出，每行格式：
    风险要素|段落编号起始|段落编号结尾|原文文本|风险判断结论及原因
    """
    records = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) < 5:
            continue

        risk_element = parts[0].strip()
        para_start = parts[1].strip()
        para_end = parts[2].strip()
        original_text = parts[3].strip()
        conclusion_and_reason = parts[4].strip()

        # 段落编号校验：仅接受纯数字或"未找到"，否则跳过该条（避免表格等误解析）
        if not _is_valid_para_id(para_start) or not _is_valid_para_id(para_end):
            continue

        # 解析段落编号
        try:
            ps = int(para_start) if para_start != "未找到" else para_start
            pe = int(para_end) if para_end != "未找到" else para_end
        except ValueError:
            continue

        # 原文过短且明显像表格单元格（如单个数字、单字段）时跳过
        if len(original_text) < 8 and original_text != "未找到相关条款":
            # 纯数字或纯单字段（无标点、无空格）视为可疑
            if original_text.isdigit() or (len(original_text) <= 4 and " " not in original_text and "，" not in original_text):
                continue

        refs = _extract_refs(conclusion_and_reason)
        risk_level = _infer_risk_level(conclusion_and_reason)

        records.append(
            AuditRecord(
                risk_element=risk_element,
                paragraph_start=ps,
                paragraph_end=pe,
                original_text=original_text,
                conclusion_and_reason=conclusion_and_reason,
                risk_level=risk_level,
                refs=refs,
            )
        )
    return records
