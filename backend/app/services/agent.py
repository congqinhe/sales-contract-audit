"""合同评审 Agent — 方案B：按模块调用大模型"""
from openai import OpenAI

from app.config import settings
from app.models.schemas import RuleCreate

# ---------------------------------------------------------------------------
# System Prompt（固定，所有模块共享）
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """你是一位资深的中国区销售合同评审专家。你的任务是根据预设的评审规则，对销售合同文本进行逐项审查，输出结构化的评审报告。

# 立场与术语映射（必须遵守）
- **我方立场**：本次审核中，我方为【乙方/卖方/供货方】（对外供货方）。所有风险判断必须以"是否对我方不利、是否增加我方义务/责任/成本、是否扩大我方赔偿范围、是否限制我方权利"为核心标准。
- **术语映射**：如合同使用"甲方/乙方""买方/卖方""需方/供方"等不同称谓，默认映射为：
  - 买方/甲方/需方/发包方/业主（如语境一致）= 对方
  - 卖方/乙方/供方/承包方（如语境一致）= 我方
- **冲突处理**：若合同中出现与上述映射不一致的明确定义，以合同明确定义为准，并在原因中说明采用了何种映射依据。
- **风险表达要求**：结论必须从我方视角表述，例如"对我方不利/我方承担…/我方责任扩大…/我方成本增加…/我方权利受限…"

# 能力边界
- 你只能基于合同文本中明确写明的内容进行评审，不得推断或假设。
- 当合同文本模糊、存在歧义时，应在评审意见中标注"待确认"。
- 你不具备访问外部系统（天眼查、SAP、信控平台等）的能力，涉及外部数据核验的评审点，你应标注"需人工核验"。

# 核心原则
1. **先识别，后判定**：对每个评审点，先提取合同中的相关条款原文，再对照风险规则进行判定。
2. **区分评审类型**：
   - identify（识别类）：仅提取信息，不判定风险
   - judge（判定类）：提取信息 + 风险判定
   - verify（核对类）：数值交叉验证
3. **引用原文**：每个评审结果必须引用合同原文作为依据，保持原文每处标点、空格完全一致，禁止改写或总结。

# 段落编号体系
- 输入的合同文本使用 `<!-- N -->` 格式标注段落编号（N 为纯数字）。
- 输出时必须通过 `paragraph_start` 和 `paragraph_end` 字段引用段落编号（`<!-- N -->` 中的 N）。
- 在 `risk_description` 中使用 `{{id:X}}` 或 `{{id:X-Y}}` 格式标注证据段落索引。
- 跨段落提取时合并段落编号范围（如 paragraph_start=12, paragraph_end=15）。
- 段落编号必须为 `<!-- N -->` 中的纯数字，不得使用表头、单元格内容作为段落编号。

# 通用约束
- **严禁幻觉**：禁止根据常识补充合同中不存在的义务或条款。
- **区分目录与正文**：目录条目仅作导航用，非实际条款。判断风险时须以正文条款为准。
- **区分表格与正文**：表格（表头、单元格）仅作数据呈现，非正文条款，不得作为风险判断的原文引用。
- **原文竖线处理**：原文中的竖线 `|` 必须替换为斜杠 `/`。
- **语言**：全中文输出。"""

# ---------------------------------------------------------------------------
# User Prompt 模板（按模块动态拼装）
# ---------------------------------------------------------------------------
USER_PROMPT_TEMPLATE = """请对以下销售合同进行【{module}】模块的评审。

## 合同信息
- 产业公司：{company}

## 评审规则
{rules_block}

## 合同文本（段落编号格式为 <!-- N -->）
{contract_text}

## 输出要求
请严格按照 JSON 数组格式输出，每个评审点一个 JSON 对象。不要输出任何其他说明文字。
JSON 数组中每个对象的字段：
- `rule_id`：规则编号（如 "LD-04"）
- `review_point`：评审点名称
- `review_type`：评审类型（"identify" / "judge" / "verify"）
- `paragraph_start`：关联原文起始段落编号（`<!-- N -->` 中的数字），未找到时为字符串 "未找到"
- `paragraph_end`：关联原文结束段落编号，未找到时为字符串 "未找到"
- `contract_quote`：零改写的合同原文引用（其中 `|` 替换为 `/`），未找到时为 "未找到相关条款"
- `extracted_info`：提取的结构化信息（JSON 对象）
- `risk_level`：风险等级 "risk" / "no_risk" / "needs_manual_review" / "not_applicable"
- `risk_description`：风险判定结论及原因，引用处使用 {{{{id:X}}}} 或 {{{{id:X-Y}}}}
- `suggestion`：评审建议（如有风险时的修改方向，无则为空字符串）

请直接输出 JSON 数组，不要包裹在 markdown 代码块中。"""


def _format_rules_block(rules: list[RuleCreate]) -> str:
    """将规则列表格式化为提示词中的 YAML 风格文本块"""
    parts = []
    for r in rules:
        lines = [
            f"### 规则 {r.rule_id}：{r.review_point}",
            f"- 评审类型：{r.review_type}",
            f"- 提取指令：\n{r.extraction_instruction}",
        ]
        if r.risk_criteria:
            lines.append(f"- 风险判定条件：\n{r.risk_criteria}")
        if r.risk_exclusion:
            lines.append(f"- 风险排除/豁免：\n{r.risk_exclusion}")
        if r.notes:
            lines.append(f"- 备注：{r.notes}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def run_module_audit_sync(
    contract_text: str,
    module: str,
    rules: list[RuleCreate],
    company: str = "通用",
) -> str:
    """
    同步调用大模型，对单个模块执行评审。
    返回 LLM 原始输出文本（JSON 字符串）。
    """
    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    rules_block = _format_rules_block(rules)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        module=module,
        company=company,
        rules_block=rules_block,
        contract_text=contract_text,
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content or ""
