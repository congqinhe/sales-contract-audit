from pydantic import BaseModel, Field
from typing import Optional, Union


class RuleCreate(BaseModel):
    risk_element: str = Field(..., description="风险要素名称")
    explanation: str = Field(..., description="风险要素解释")
    risk_exclusion: str = Field(default="", description="风险排除描述，说明何种情形应排除、不作为风险")


class Rule(RuleCreate):
    id: str


class AuditRecord(BaseModel):
    """单条审核结果"""
    risk_element: str
    paragraph_start: Union[str, int]
    paragraph_end: Union[str, int]
    original_text: str
    conclusion_and_reason: str
    risk_level: Optional[str] = "中风险"  # 低/中/高
    refs: list[dict] = Field(default_factory=list)  # [{"start": 46, "end": 51}, ...]


class ContractParseResult(BaseModel):
    """PDF 解析结果"""
    paragraphs: list[dict]  # [{"id": 1, "text": "..."}, ...]
    full_text: str  # 带编号的全文，供 Agent 使用


class AuditRequest(BaseModel):
    contract_text: str = Field(..., description="合同全文（已分段编号）")
    risk_element: str
    explanation: str


class AuditResponse(BaseModel):
    records: list[AuditRecord]
    raw_output: Optional[str] = None
