"""方案B：模块级审核服务 — 单模块调用 + 全量并行调用"""
import asyncio
import logging
from typing import Any, Optional

from app.config import settings
from app.data.rules_data import MODULES, get_rules_by_module
from app.models.schemas import AuditRecord
from app.services.agent import run_module_audit_sync
from app.services.output_parser import parse_module_output
from app.services.slicer import slice_contract

logger = logging.getLogger(__name__)


def _run_module_single(
    contract_text: str,
    module: str,
    company: str = "通用",
) -> tuple[list[AuditRecord], str]:
    """
    对单个模块执行评审（同步）。
    自动处理长合同切片：当段落数超过 chunk_size 时分段调用再合并。
    """
    rules = get_rules_by_module(module, company)
    if not rules:
        return [], ""

    chunks = slice_contract(
        contract_text,
        chunk_size=settings.audit_chunk_size,
        overlap=settings.audit_chunk_overlap,
    )

    if len(chunks) <= 1:
        raw = run_module_audit_sync(contract_text, module, rules, company)
        records = parse_module_output(raw, module)
        if not raw.strip():
            logger.warning("[%s] LLM 返回空内容", module)
        elif not records:
            logger.warning("[%s] 解析出 0 条记录, raw_len=%d, tail=%.200s", module, len(raw), raw[-200:])
        return records, raw

    all_records: list[AuditRecord] = []
    raw_parts: list[str] = []

    for i, chunk in enumerate(chunks):
        raw = run_module_audit_sync(chunk.chunk_text, module, rules, company)
        records = parse_module_output(raw, module)
        if not raw.strip():
            logger.warning("[%s] chunk %d/%d LLM 返回空内容", module, i + 1, len(chunks))
        elif not records:
            logger.warning(
                "[%s] chunk %d/%d 解析出 0 条记录, raw_len=%d, tail=%.200s",
                module, i + 1, len(chunks), len(raw), raw[-200:],
            )
        all_records.extend(records)
        raw_parts.append(f"# Chunk {i+1}/{len(chunks)} (段落 {chunk.start_id}-{chunk.end_id})\n{raw}")

    merged = _deduplicate_records(all_records)
    return merged, "\n\n".join(raw_parts)


def _deduplicate_records(records: list[AuditRecord]) -> list[AuditRecord]:
    """按 (rule_id, paragraph_start, paragraph_end) 去重，有实际段落引用的优先"""
    seen: set[tuple] = set()
    by_rule: dict[str, list[AuditRecord]] = {}

    for r in records:
        key = (r.rule_id, r.paragraph_start, r.paragraph_end)
        if key in seen:
            continue
        seen.add(key)
        by_rule.setdefault(r.rule_id, []).append(r)

    merged: list[AuditRecord] = []
    for rule_id, recs in by_rule.items():
        found = [r for r in recs if r.paragraph_start != "未找到"]
        not_found = [r for r in recs if r.paragraph_start == "未找到"]
        if found:
            merged.extend(found)
        elif not_found:
            merged.append(not_found[0])
    return merged


async def run_module_audit(
    contract_text: str,
    module: str,
    company: str = "通用",
) -> tuple[list[AuditRecord], str]:
    """异步包装：在线程池中执行同步 LLM 调用"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _run_module_single, contract_text, module, company
    )


async def run_full_audit(
    contract_text: str,
    company: str = "通用",
    modules: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    全量审核：所有模块并行调用，返回结构化报告。

    返回:
        {
            "modules": { "模块名": [AuditRecord, ...], ... },
            "summary": { "total_rules": N, "risk_count": N, ... },
            "raw_output": "..."
        }
    """
    target_modules = modules or list(MODULES)

    tasks = [
        run_module_audit(contract_text, m, company)
        for m in target_modules
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    module_records: dict[str, list[AuditRecord]] = {}
    raw_parts: list[str] = []
    total_rules = 0
    risk_count = 0
    needs_review_count = 0
    no_risk_count = 0

    for module_name, result in zip(target_modules, results):
        if isinstance(result, Exception):
            logger.error("[%s] 模块审核异常: %s", module_name, result)
            module_records[module_name] = []
            raw_parts.append(f"# {module_name}\n[ERROR] {str(result)}")
            continue

        records, raw = result
        module_records[module_name] = records
        raw_parts.append(f"# {module_name}\n{raw}")

        for r in records:
            total_rules += 1
            if r.risk_level == "risk":
                risk_count += 1
            elif r.risk_level == "needs_manual_review":
                needs_review_count += 1
            elif r.risk_level == "no_risk":
                no_risk_count += 1

    return {
        "modules": module_records,
        "summary": {
            "total_rules": total_rules,
            "risk_count": risk_count,
            "needs_review_count": needs_review_count,
            "no_risk_count": no_risk_count,
        },
        "raw_output": "\n\n".join(raw_parts),
    }
