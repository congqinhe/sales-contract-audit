"""PDF 解析：调用正泰 AI upload-file + fetch-file 接口"""
import json
import time

import httpx

from app.config import settings


def _log(path: str, msg: str, data: dict) -> None:
    # #region agent log
    try:
        with open("/Users/hecongqin/Program/sales-contract-audit/.cursor/debug-be0578.log", "a") as f:
            f.write(json.dumps({"sessionId":"be0578","location":path,"message":msg,"data":data,"hypothesisId":"H1","timestamp":__import__("time").time()*1000}) + "\n")
    except Exception:
        pass
    # #endregion


def parse_pdf(file_content: bytes, filename: str = "contract.pdf") -> str:
    """
    上传 PDF 到正泰 API，轮询获取解析结果。
    返回解析后的文本内容（Markdown 或纯文本）。
    """
    base = settings.openai_base_url.rstrip("/")
    upload_url = f"{base}/upload-file"
    api_key = settings.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY 未配置")

    # 1. 上传 PDF（文档要求必填: file, model。model 支持 MinerU）
    _log("pdf_parser:upload:before", "upload start", {"url": upload_url, "file_len": len(file_content), "filename": filename})
    with httpx.Client(timeout=60.0) as client:
        files = {"file": (filename, file_content, "application/pdf")}
        data_form = {"model": "MinerU"}  # 必填：模型名称
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = client.post(upload_url, files=files, data=data_form, headers=headers)
        _log("pdf_parser:upload:response", "upload response", {"status": resp.status_code, "body": resp.text[:500]})
        resp.raise_for_status()
        data = resp.json()

    # 响应应包含 id 用于轮询（兼容不同接口返回格式）
    inner = data.get("data") if isinstance(data.get("data"), dict) else {}
    file_id = data.get("id") or data.get("file_id") or inner.get("id") or inner.get("file_id")
    if not file_id:
        raise ValueError(f"上传响应缺少 id 字段，请参考文档: {list(data.keys())}")

    # 2. 轮询获取解析结果（queue -> pending -> success，大文件可能需 2–3 分钟）
    fetch_url = f"{base}/fetch-file"
    max_attempts = 120  # 最多约 4 分钟
    poll_interval = 2

    for attempt in range(max_attempts):
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                fetch_url,
                params={"id": file_id},
                headers={"Authorization": f"Bearer {api_key}"},
            )
        resp.raise_for_status()
        result = resp.json()
        if (attempt + 1) <= 3 or (attempt + 1) % 15 == 0 or result.get("status") not in ("queue", "pending"):
            _log("pdf_parser:fetch", "fetch response", {"attempt": attempt + 1, "status": result.get("status"), "result_url_empty": not (result.get("result_url") or "").strip()})

        # 根据接口文档，可能返回 content、result、data、result_url 等
        raw = result.get("content") or result.get("result") or result.get("data")
        if raw is not None:
            if isinstance(raw, str) and raw.strip():
                _log("pdf_parser:fetch:success", "got content", {"len": len(raw)})
                return raw
            if isinstance(raw, dict):
                txt = raw.get("content") or raw.get("text") or raw.get("result")
                if isinstance(txt, str) and txt.strip():
                    _log("pdf_parser:fetch:success", "got content from dict", {"len": len(txt)})
                    return txt

        # result_url：完成时为 MinIO 预签名/公开 URL，勿带 Authorization（会导致 Connection reset）
        result_url = result.get("result_url")
        if result_url and isinstance(result_url, str) and result_url.strip():
            _log("pdf_parser:fetch:result_url", "fetching result_url", {"url": result_url[:100]})
            with httpx.Client(timeout=60.0) as client:
                r2 = client.get(result_url)  # 预签名 URL 不需要 Bearer
                r2.raise_for_status()
                ct = (r2.headers.get("content-type") or "").lower()
                if "json" in ct:
                    content = r2.json()
                    txt = content.get("content") or content.get("text") or content.get("result") if isinstance(content, dict) else None
                    if isinstance(txt, str) and txt.strip():
                        _log("pdf_parser:fetch:success", "got content from result_url", {"len": len(txt)})
                        return txt
                else:
                    content = r2.text
                    if content and content.strip():
                        _log("pdf_parser:fetch:success", "got content from result_url", {"len": len(content)})
                        return content

        # 若仍在处理（queue/pending/processing），继续轮询
        status = (result.get("status") or "").lower()
        if status in ("queue", "pending", "processing"):
            time.sleep(poll_interval)
            continue
        if "fail" in status or "error" in status:
            err = result.get("error_message") or result.get("message") or "PDF 解析失败"
            raise ValueError(str(err))

        time.sleep(poll_interval)

    _log("pdf_parser:fetch:timeout", "max attempts reached", {"attempts": max_attempts})
    raise TimeoutError("PDF 解析超时（大文件需 2–3 分钟），请稍后重试")
