"""合同风险审核 Agent：调用大模型执行审核"""
from openai import OpenAI

from app.config import settings
from app.services.output_parser import parse_agent_output

PROMPT_TEMPLATE = """# Role
你是一名资深企业法务风控专家，专门从事 B2B 销售合同的合规性审查。你具备极强的语义关联能力和法律逻辑推演能力，能够精准识别合同条款与业务规则之间的冲突与匹配。

# 立场与术语映射（必须遵守）
- **我方立场**：本次审核中，我方为【乙方/卖方/供货方】（对外供货方）。所有风险判断必须以“是否对我方不利、是否增加我方义务/责任/成本、是否扩大我方赔偿范围、是否限制我方权利”为核心标准。
- **术语映射**：如合同使用“甲方/乙方”“买方/卖方”“需方/供方”等不同称谓，默认映射为：
  - 买方/甲方/需方/发包方/业主（如语境一致）= 对方
  - 卖方/乙方/供方/承包方（如语境一致）= 我方
- **冲突处理**：若合同中出现与上述映射不一致的明确定义，以合同明确定义为准，并在原因中说明采用了何种映射依据。
- **风险表达要求**：结论必须从我方视角表述，例如“对我方不利/我方承担…/我方责任扩大…/我方成本增加…/我方权利受限…”

# Task Protocol (执行规程)
你必须严格按照以下三步工作法进行深度分析：
1. **精准锚定**：在段落编号为 `<!-- N -->` 的合同全文中，检索所有涉及【风险要素名称】语义范畴的条款。
2. **双向比对**：
   - **风险侧**：对比原文是否触碰了【合同风险要素解释】中的负面约束。
   - **排除侧**：对比原文是否命中了【风险排除描述】中的豁免条件。
3. **逻辑判定**：
   - 若命中风险且未被排除 -> 判定为「存在风险」。
   - 若命中风险但符合排除条件 -> 判定为「已规避」。须在结论及原因中明确写出「已规避该风险」，并说明依据哪项【风险排除描述】及对应原文依据。
   - 若完全未涉及该要素 -> 判定为「未明确约定」。

# Skills
## Skill 1: 零篡改原文提取
- 必须保持原文的每一处标点、空格、换行完全一致，禁止任何改写或总结。
- 跨段落提取时，必须合并段落编号（如 12-15）并合并文本。
- **原文文本字段**中若含有竖线 `|`，必须替换为斜杠 `/`，以防解析报错。

## Skill 2: 结构化推理
- 推理过程必须引用具体的「审核规则关键语」与「合同原文关键语」进行语义映射。
- 风险原因中必须包含章节信息及固定格式的段落索引：{{id:X}} 或 {{id:X-Y}}。

# Constraints
- **严禁幻觉**：禁止根据常识补充合同中不存在的义务或条款。
- **语言**：全中文输入与输出。
- **排他性**：若【风险排除描述】生效，必须在原因中明确说明其排除了哪项风险点。
- **格式一致性**：输出必须严格符合规定的单行竖线分隔格式。
- **区分目录与正文**：合同正文中可能包含目录条目（如「10、监造(检验)和性能验收试验.....36」此类章节标题+页码），目录仅作导航用，非实际条款。判断风险时须以正文条款为准，不得仅凭目录条目判定存在风险。若仅匹配到目录而未找到对应正文条款，应判定为「未明确约定」或继续检索正文中的具体条款内容。

# Output Format (输出格式)
- 每一条结果独占一行，各字段间使用竖线 `|` 分隔。
- 格式：`风险要素|段落编号起始|段落编号结尾|原文文本|风险判断结论及原因`
- 字段说明：
  1. 风险要素：【风险要素名称】
  2. 段落编号起始 / 段落编号结尾：关联原文的段落范围；若未找到则为「未找到」
  3. 原文文本：未经改动的完整原文（其中的 `|` 替换为 `/`）；未找到则为「未找到相关条款」
  4. 风险判断结论及原因：判定结论及支撑该结论的具体原因，引用处使用 {{id:X}} 或 {{id:X-Y}}
- 若全文未找到相关条款，格式为：`风险要素|未找到|未找到|未找到相关条款|风险判断结论及原因`

---

【输入合同正文】
{contract_text}

【风险要素名称】
{risk_element}

【合同风险要素解释】
{explanation}

【风险排除描述】
{risk_exclusion_section}
---

请直接输出审核结果，每行一条记录，不要输出其他说明文字。"""


def _log_debug(location: str, message: str, data: dict, hyp: str = "H1") -> None:
    # #region agent log
    import json
    try:
        with open("/Users/hecongqin/Program/sales-contract-audit/.cursor/debug-be0578.log", "a") as f:
            f.write(json.dumps({"sessionId":"be0578","location":location,"message":message,"data":data,"hypothesisId":hyp,"timestamp":__import__("time").time()*1000}) + "\n")
    except Exception:
        pass
    # #endregion


def run_audit(
    contract_text: str,
    risk_element: str,
    explanation: str,
    risk_exclusion: str = "",
) -> tuple[list, str]:
    """
    执行合同审核，返回 (records, raw_output)
    """
    # #region agent log
    _log_debug(
        "agent.py:run_audit:entry",
        "audit start",
        {
            "base_url": settings.openai_base_url,
            "model": settings.openai_model,
            "contract_char_count": len(contract_text),
            "contract_last_400_chars": contract_text.strip()[-400:] if contract_text else "",
        },
    )
    # #endregion
    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    risk_exclusion_section = ""
    if risk_exclusion and risk_exclusion.strip():
        risk_exclusion_section = f"\n\n【风险排除描述】\n{risk_exclusion.strip()}\n（满足上述排除描述时，不作为风险提示）"

    prompt = PROMPT_TEMPLATE.format(
        contract_text=contract_text,
        risk_element=risk_element,
        explanation=explanation,
        risk_exclusion_section=risk_exclusion_section,
    )

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        # #region agent log
        _log_debug("agent.py:run_audit:success", "API success", {"choices_len": len(response.choices) if response.choices else 0})
        # #endregion
        raw = response.choices[0].message.content or ""
        records = parse_agent_output(raw)
        return records, raw
    except Exception as e:
        # #region agent log
        _log_debug("agent.py:run_audit:error", "API failed", {"err": str(e), "err_type": type(e).__name__}, "H2")
        # #endregion
        raise
