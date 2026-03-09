"""切片审核：将长合同分段调用大模型，合并结果"""
from app.models.schemas import AuditRecord
from app.services.agent import run_audit
from app.services.slicer import slice_contract, SliceChunk


def _is_not_found_record(r: AuditRecord) -> bool:
    """是否为「未找到」类记录"""
    return r.paragraph_start == "未找到" or r.paragraph_end == "未找到"


def _merge_records(all_records: list[list[AuditRecord]]) -> list[AuditRecord]:
    """
    合并多 chunk 的审核结果：
    - 同一 risk_element 下，有实际段落引用的记录优先，去掉重复的「未找到」
    - 按 (risk_element, para_start, para_end) 去重
    """
    seen: set[tuple[str, str | int, str | int]] = set()
    merged: list[AuditRecord] = []
    # 按 risk_element 分组，先收集有实际引用的，再处理「未找到」
    by_element: dict[str, list[AuditRecord]] = {}
    for chunk_records in all_records:
        for r in chunk_records:
            key = (r.risk_element, r.paragraph_start, r.paragraph_end)
            if key in seen:
                continue
            seen.add(key)
            if r.risk_element not in by_element:
                by_element[r.risk_element] = []
            by_element[r.risk_element].append(r)

    for risk_element, recs in by_element.items():
        found_recs = [r for r in recs if not _is_not_found_record(r)]
        not_found_recs = [r for r in recs if _is_not_found_record(r)]
        if found_recs:
            merged.extend(found_recs)
        else:
            # 全部为「未找到」时保留一条
            if not_found_recs:
                merged.append(not_found_recs[0])

    return merged


def run_audit_sliced(
    contract_text: str,
    risk_element: str,
    explanation: str,
    risk_exclusion: str = "",
    chunk_size: int = 80,
    overlap: int = 10,
) -> tuple[list[AuditRecord], str]:
    """
    切片审核：将合同按段落切分后逐段调用 run_audit，合并结果。

    当合同段落数 <= chunk_size 时，不切片，直接调用 run_audit。
    """
    chunks = slice_contract(contract_text, chunk_size=chunk_size, overlap=overlap)
    if len(chunks) <= 1:
        records, raw = run_audit(contract_text, risk_element, explanation, risk_exclusion)
        return records, raw

    all_records: list[list[AuditRecord]] = []
    raw_parts: list[str] = []
    for i, chunk in enumerate(chunks):
        records, raw = run_audit(
            chunk.chunk_text,
            risk_element,
            explanation,
            risk_exclusion,
        )
        all_records.append(records)
        raw_parts.append(f"# Chunk {i+1}/{len(chunks)} (段落 {chunk.start_id}-{chunk.end_id})\n{raw}")

    merged = _merge_records(all_records)
    combined_raw = "\n\n".join(raw_parts)
    return merged, combined_raw
