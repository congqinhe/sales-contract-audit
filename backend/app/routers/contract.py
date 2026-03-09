"""合同文本输入与审核 API"""
import re
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import AuditRecord, AuditResponse
from app.services.agent import run_audit
from app.services.pdf_parser import parse_pdf
from app.services.text_parser import parse_text, text_to_paragraphs

router = APIRouter(prefix="/api/contract", tags=["contract"])


@router.post("/inspect")
async def inspect_contract_text(contract_text: str = Form(...)):
    """
    验证接口：检查传入的合同全文统计信息，用于排查 AI 是否只看到前几行的疑问。
    返回：字符数、行数、段落数、首尾片段。
    """
    lines = [ln.strip() for ln in contract_text.strip().split("\n") if ln.strip()]
    # 近似段落数（按 <!-- N --> 计）
    para_count = sum(1 for ln in lines if re.match(r"^\s*<!--\s*\d+\s*-->", ln))
    if para_count == 0:
        para_count = len(lines)
    first_300 = contract_text.strip()[:300] if contract_text else ""
    last_300 = contract_text.strip()[-300:] if contract_text else ""
    return {
        "char_count": len(contract_text),
        "line_count": len(lines),
        "para_count_approx": para_count,
        "first_300_chars": first_300,
        "last_300_chars": last_300,
    }


@router.post("/parse")
async def parse_contract_text(
    content: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    """
    解析合同文本。支持三种方式：
    1. content: 直接粘贴的文本（带 <!-- N --> 格式）
    2. file: 上传 TXT 或 PDF 文件（PDF 调用正泰 AI 解析）
    """
    text = None
    if content and content.strip():
        text = content.strip()
    elif file and file.filename:
        file_ext = file.filename.lower().split(".")[-1]
        file_bytes = await file.read()
        if file_ext == "txt":
            text = file_bytes.decode("utf-8", errors="ignore").strip()
        elif file_ext == "pdf":
            try:
                text = parse_pdf(file_bytes, file.filename)
                # PDF 解析结果无 <!-- N -->，必须为每段加上标志位
                result = text_to_paragraphs(text)
                if len(result["paragraphs"]) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="PDF 解析未得到有效内容，请检查文件",
                    )
                return {
                    "paragraphs": result["paragraphs"],
                    "full_text": result["full_text"],
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"PDF 解析失败: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="仅支持 .txt 或 .pdf 文件")
    if not text:
        raise HTTPException(
            status_code=400,
            detail="请粘贴合同文本或上传 TXT 文件",
        )

    # 尝试 <!-- N --> 格式；若无则按纯文本分段
    result = parse_text(text)
    if len(result["paragraphs"]) == 0:
        result = text_to_paragraphs(text)
    if len(result["paragraphs"]) == 0:
        raise HTTPException(
            status_code=400,
            detail="未解析到有效段落。TXT 需包含 <!-- N --> 格式；PDF 将自动解析。",
        )
    return {
        "paragraphs": result["paragraphs"],
        "full_text": result["full_text"],
    }


@router.post("/audit")
async def audit_contract(
    contract_text: str = Form(...),
    risk_element: str = Form(...),
    explanation: str = Form(...),
    risk_exclusion: str = Form(default=""),
):
    """
    对已解析的合同全文执行单条规则审核。
    contract_text 应为 parse 接口返回的 full_text。
    """
    if not contract_text or not risk_element:
        raise HTTPException(status_code=400, detail="缺少 contract_text 或 risk_element")
    try:
        records: list[AuditRecord]
        raw: str
        records, raw = run_audit(
            contract_text, risk_element, explanation, risk_exclusion
        )
        return AuditResponse(records=records, raw_output=raw)
    except Exception as e:
        err = str(e)
        # #region agent log
        import json
        try:
            with open("/Users/hecongqin/Program/sales-contract-audit/.cursor/debug-be0578.log", "a") as f:
                f.write(json.dumps({"sessionId":"be0578","location":"contract.py:audit:catch","message":"audit exception","data":{"err":err[:500]}, "hypothesisId":"H2","timestamp":__import__("time").time()*1000}) + "\n")
        except Exception:
            pass
        # #endregion
        if "429" in err or "速率限制" in err or "rate limit" in err.lower():
            raise HTTPException(
                status_code=429,
                detail="智谱 API 请求过于频繁，请稍后再试（通常 1 分钟后可恢复）",
            )
        raise HTTPException(status_code=500, detail=f"审核失败: {err}")
