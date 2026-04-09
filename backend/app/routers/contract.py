"""合同文本输入与审核 API — 方案B"""
import re
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import AuditRecord, AuditResponse, FullAuditResponse
from app.services.audit_module import run_module_audit, run_full_audit
from app.services.text_parser import parse_text, text_to_paragraphs

router = APIRouter(prefix="/api/contract", tags=["contract"])


@router.post("/inspect")
async def inspect_contract_text(contract_text: str = Form(...)):
    """验证接口：检查传入的合同全文统计信息"""
    lines = [ln.strip() for ln in contract_text.strip().split("\n") if ln.strip()]
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
    解析合同文本。支持：
    1. content: 直接粘贴的文本（带 <!-- N --> 格式）
    2. file: 上传 TXT 文件
    """
    text = None
    if content and content.strip():
        text = content.strip()
    elif file and file.filename:
        file_ext = file.filename.lower().split(".")[-1]
        if file_ext != "txt":
            raise HTTPException(status_code=400, detail="仅支持 .txt 文件")
        file_bytes = await file.read()
        text = file_bytes.decode("utf-8", errors="ignore").strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="请粘贴合同文本或上传 TXT 文件",
        )

    result = parse_text(text)
    if len(result["paragraphs"]) == 0:
        result = text_to_paragraphs(text)
    if len(result["paragraphs"]) == 0:
        raise HTTPException(
            status_code=400,
            detail="未解析到有效段落，TXT 文件需包含 <!-- N --> 段落编号格式。",
        )
    return {
        "paragraphs": result["paragraphs"],
        "full_text": result["full_text"],
    }


# -----------------------------------------------------------------------
# 方案B：按模块审核
# -----------------------------------------------------------------------

@router.post("/audit/module")
async def audit_by_module(
    contract_text: str = Form(...),
    module: str = Form(...),
    company: Optional[str] = Form(default="通用"),
):
    """对已解析的合同执行单个模块的评审"""
    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="缺少 contract_text")
    if not module.strip():
        raise HTTPException(status_code=400, detail="缺少 module")
    try:
        records, raw = await run_module_audit(
            contract_text, module, company or "通用"
        )
        return AuditResponse(records=records, raw_output=raw)
    except Exception as e:
        _handle_audit_error(e)


@router.post("/audit/full")
async def audit_full(
    contract_text: str = Form(...),
    company: Optional[str] = Form(default="通用"),
):
    """全量审核：所有模块并行调用"""
    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="缺少 contract_text")
    try:
        result = await run_full_audit(contract_text, company or "通用")
        module_records = {
            k: [r.model_dump() for r in v]
            for k, v in result["modules"].items()
        }
        return {
            "modules": module_records,
            "summary": result["summary"],
            "raw_output": result["raw_output"],
        }
    except Exception as e:
        _handle_audit_error(e)


def _handle_audit_error(e: Exception):
    err = str(e)
    if "429" in err or "速率限制" in err or "rate limit" in err.lower():
        raise HTTPException(
            status_code=429,
            detail="API 请求过于频繁，请稍后再试（通常 1 分钟后可恢复）",
        )
    raise HTTPException(status_code=500, detail=f"审核失败: {err}")
