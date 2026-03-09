"""合同切片：按段落切分 full_text，用于分段审核以缓解长文注意力问题"""
import re
from dataclasses import dataclass


@dataclass
class SliceChunk:
    """单个切片"""
    chunk_text: str
    start_id: int
    end_id: int


def slice_contract(
    full_text: str,
    chunk_size: int = 80,
    overlap: int = 10,
) -> list[SliceChunk]:
    """
    将合同全文按段落切分成多个 chunk，相邻 chunk 有重叠段落。

    Args:
        full_text: 带 <!-- N --> 段落编号的全文
        chunk_size: 每个 chunk 的段落数
        overlap: 相邻 chunk 之间的重叠段落数

    Returns:
        切片列表，每个切片包含 chunk_text、start_id、end_id
    """
    lines_with_id: list[tuple[int, str]] = []
    for line in full_text.strip().split("\n"):
        line = line.rstrip("\r")
        if not line.strip():
            continue
        m = re.match(r"^\s*<!--\s*(\d+)\s*-->\s*(.*)$", line)
        if m:
            pid = int(m.group(1))
            lines_with_id.append((pid, line))

    if not lines_with_id:
        return [SliceChunk(chunk_text=full_text, start_id=0, end_id=0)]

    # 段落数少于 chunk_size 时不再切片
    if len(lines_with_id) <= chunk_size:
        start_id = lines_with_id[0][0]
        end_id = lines_with_id[-1][0]
        return [SliceChunk(chunk_text=full_text.strip(), start_id=start_id, end_id=end_id)]

    step = max(1, chunk_size - overlap)
    chunks: list[SliceChunk] = []
    i = 0
    while i < len(lines_with_id):
        chunk_lines = lines_with_id[i : i + chunk_size]
        if not chunk_lines:
            break
        start_id = chunk_lines[0][0]
        end_id = chunk_lines[-1][0]
        chunk_text = "\n".join(ln for _, ln in chunk_lines)
        chunks.append(SliceChunk(chunk_text=chunk_text, start_id=start_id, end_id=end_id))
        i += step

    return chunks
