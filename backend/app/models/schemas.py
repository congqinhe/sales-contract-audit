from pydantic import BaseModel, Field
from typing import Any, Literal, Optional, Union


# ---------------------------------------------------------------------------
# 规则模型（方案B：结构化规则）
# ---------------------------------------------------------------------------

class RuleCreate(BaseModel):
    rule_id: str = Field(..., description="规则唯一编号，如 LD-01, IP-02")
    module: str = Field(..., description="所属部门模块，如 履约交付平台, 法务部")
    review_point: str = Field(..., description="评审点名称")
    review_type: Literal["identify", "judge", "verify"] = Field(
        ..., description="评审类型：identify=识别提取, judge=判定风险, verify=数值核对"
    )
    shared_modules: list[str] = Field(
        default_factory=list,
        description="规则共享到的其他模块（除 module 主模块外），支持一条规则在多个模块中展示",
    )
    applies_to: Optional[str] = Field(
        default=None, description="适用产业公司：低压/诺雅克/输配电, None=通用"
    )
    extraction_instruction: str = Field(..., description="从合同中提取什么信息")
    risk_criteria: Optional[str] = Field(
        default=None, description="风险判定条件（identify 类为 None）"
    )
    risk_exclusion: str = Field(default="", description="风险排除/豁免条件")
    notes: str = Field(default="", description="特殊说明与判定补充")


class Rule(RuleCreate):
    id: str


# ---------------------------------------------------------------------------
# 审核结果模型（方案B：JSON 结构化输出）
# ---------------------------------------------------------------------------

class AuditRecord(BaseModel):
    """单条评审结果"""
    rule_id: str
    module: str = ""
    review_point: str = ""
    review_type: str = "judge"
    paragraph_start: Union[str, int] = Field(
        description="关联原文起始段落编号（<!-- N --> 中的 N），未找到时为字符串 '未找到'"
    )
    paragraph_end: Union[str, int] = Field(
        description="关联原文结束段落编号"
    )
    contract_quote: str = Field(default="", description="零改写合同原文引用")
    extracted_info: dict[str, Any] = Field(
        default_factory=dict, description="提取的结构化信息"
    )
    risk_level: str = Field(
        default="no_risk",
        description="risk / no_risk / needs_manual_review / not_applicable"
    )
    risk_description: str = Field(default="", description="风险判定结论及原因")
    suggestion: str = Field(default="", description="评审建议")
    refs: list[dict] = Field(
        default_factory=list, description='段落引用 [{"start": 46, "end": 51}]'
    )
    evidence_spans: list[dict[str, Any]] = Field(
        default_factory=list,
        description="本规则关联的全部证据段落区间（可多项），与 paragraph 主引用配合用于防漏检",
    )


class ContractParseResult(BaseModel):
    """PDF 解析结果"""
    paragraphs: list[dict]
    full_text: str


class AuditRequest(BaseModel):
    contract_text: str = Field(..., description="合同全文（已分段编号）")
    module: Optional[str] = None
    company: Optional[str] = None


class AuditResponse(BaseModel):
    records: list[AuditRecord]
    raw_output: Optional[str] = None


class FullAuditResponse(BaseModel):
    modules: dict[str, list[AuditRecord]] = Field(
        default_factory=dict, description="按模块分组的评审结果"
    )
    summary: dict[str, Any] = Field(default_factory=dict)
    raw_output: Optional[str] = None
