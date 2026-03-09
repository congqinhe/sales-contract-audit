"""从规范格式的 MD/TXT 中解析段落（<!-- N --> 格式）"""
import re


def text_to_paragraphs(content: str) -> dict:
    """
    将纯文本/Markdown 转为段落格式，每段首行加上 <!-- N --> 标志位。
    用于 PDF 解析等无编号文本的后续处理。
    优先按空行分段；若无非空行则按单行分段。
    """
    raw_blocks = re.split(r"\n\s*\n", content.strip())
    # 若仅一段且含多行，改为按单行分段（适配逐行返回的 PDF）
    if len(raw_blocks) == 1 and "\n" in raw_blocks[0]:
        raw_blocks = [ln.strip() for ln in raw_blocks[0].split("\n") if ln.strip()]
    paragraphs = []
    full_lines = []
    pid = 1
    for block in raw_blocks:
        block = block.strip().replace("\r", "")
        if not block:
            continue
        text = "\n".join(line.strip() for line in block.split("\n") if line.strip())
        if not text:
            continue
        para = {"id": pid, "text": text, "page": 1}
        paragraphs.append(para)
        full_lines.append(f"<!-- {pid} --> {text}")
        pid += 1
    full_text = "\n".join(full_lines)
    return {"paragraphs": paragraphs, "full_text": full_text}


def parse_text(content: str) -> dict:
    """
    解析带 <!-- N --> 编号的合同文本，返回段落列表和全文。
    content 可为粘贴的文本或从 TXT 文件读取的内容。
    """
    paragraphs = []
    full_lines = []

    for line in content.split("\n"):
        line = line.rstrip("\r")
        m = re.match(r"^\s*<!--\s*(\d+)\s*-->\s*(.*)$", line)
        if m:
            pid = int(m.group(1))
            text = m.group(2).strip()
            para = {"id": pid, "text": text or line.strip(), "page": 1}
            paragraphs.append(para)
            full_lines.append(f"<!-- {pid} -->{para['text']}")

    full_text = "\n".join(full_lines)
    return {"paragraphs": paragraphs, "full_text": full_text}
