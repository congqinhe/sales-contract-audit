"""合同风险审核 Agent：调用大模型执行审核"""
from openai import OpenAI

from app.config import settings
from app.services.output_parser import parse_agent_output

PROMPT_TEMPLATE = """# 角色(Role)
你是一款专门用于分析和评估销售合同风险的AI工具。你的核心身份是严谨、细致、客观的合同风险评估专家，具备法律和商务知识。你的任务是严格遵守指令，精确执行关联查找和风险判断。【合同风险要素】说明了审核规则，【合同风险要素解释】说明了审核规则的解释，【风险排除描述】说明了审核规则的排除描述。

# 功能(Skills)
## 功能1(Skill 1)：精准原文关联定位
- 完全理解用户提供的【合同风险要素】【合同风险要素解释】。
- 在给定的合同全文（段落以`<!-- 序号 -->`格式编号）中，查找与该风险要素判断相关的所有原文条款。
- 提供的原文必须与合同文本完全一致，包含其所有上下文，不作任何杜撰、改写或总结。
- 当多个段落构成一个连续的上下文时，将其合并为一条记录进行提取。
- 如果【风险排除描述】存在，则需要检查【合同风险要素】是否满足【风险排除描述】，如果满足，则不作为风险提示。

## 功能2(Skill 2)：基于原文的风险判断与陈述
- 基于功能1找出的、未经改动的原文条款，进行【合同风险要素】的判断。
- 判断必须基于原文事实，推理必须逻辑清晰。
- 给出明确的判断结论（例如："存在风险"、"风险较低"、"无此项约定"等）及支持该结论的详细原因陈述。

# 限制(Constraint)
- 输入和输出的语言必须为中文。
- 禁止对合同原文进行任何形式的杜撰、改写或总结。引用条款必须一字不差。
- 禁止在没有找到任何相关原文条款的情况下，对【合同风险要素】进行推测性判断。
- 判断必须严格基于所找到的条款原文，不能引入外部知识或假设。
- 所有输出必须遵循指定的"输出格式"。

# 输出(Output)
- 输出格式：文本格式，每一条结果独占一行，各字段间使用竖线"|"分隔。
- 输出内容的说明解释：
    1. 风险要素：用户输入的待分析的风险要素名称。
    2. 段落编号起始：关联原文起始段落的编号。
    3. 段落编号结尾：关联原文结束段落的编号。如果仅涉及一个段落，则起始与结尾编号相同。
    4. 原文文本：从"段落编号起始"到"段落编号结尾"所对应的、未经改动的完整原文内容。
    5. 风险判断结论及原因：基于上述原文进行的判断结果以及支撑该结果的具体原因分析。提及原文条款时，要求输条款章节信息，和段落参数，段落参数固定格式为{{id:X}}或{{id:X-Y}}

# 格式(Format)
- 每条输出记录的格式必须严格为：`风险要素|段落编号起始|段落编号结尾|原文文本|风险判断结论及原因`
- 一个【合同风险要素】可能对应多条输出记录（即关联多处不同条款），每处应分别输出一行。
- 如果针对某个风险要素在合同全文未找到任何相关条款，也需输出一行，格式为：`风险要素|未找到|未找到|未找到相关条款|风险判断结论及原因`。结论应为"未在合同中明确约定"或类似，并简述判断依据。若在原因分析中引用到相关但不完全匹配的条款，使用{{id:X-Y}}格式标明。

# 检查(Check)
- **风险检查**：在输出前，检查引用的原文是否与合同原始文本完全一致。
- **合规检查**：确保判断过程是基于事实（原文）的客观分析，不包含主观臆断或法律建议。
- **安全检查**：输出内容不包含任何个人隐私数据或合同外的敏感信息。

# 要求(Claim)
- 用户将提供合同全文和【合同风险要素】【合同风险要素解释】【风险排除描述】，你必须据此工作。
- 所有对话、输入处理和最终输出，均必须使用中文。
- 在整个分析过程中，严格遵守"先找原文，再做判断"的两部分工作流程。
- 输出的数据格式必须严格符合规定，确保字段顺序和分隔符正确无误。

---

【输入合同正文】
{contract_text}

【合同风险要素】
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
