"""内置审核规则数据（风险要素名称、解释、排除描述）"""
from app.models.schemas import RuleCreate

BUILTIN_RULES: list[RuleCreate] = [
    RuleCreate(
        risk_element="履约交付平台 - 未约定指定交货方式",
        explanation="合同文本中未识别出车板交货、主变基础交货、主变基础就位任意一项表述，触发风险",
        risk_exclusion="合同已明确约定车板交货、主变基础交货、主变基础就位中至少一项交货方式",
    ),
    RuleCreate(
        risk_element="履约交付平台 - 乙方承担卸货责任",
        explanation="合同约定乙方/卖方承担卸货义务，触发风险",
        risk_exclusion="合同无乙方/卖方承担卸货义务的相关表述",
    ),
    RuleCreate(
        risk_element="履约交付平台 - 乙方承担卸车货损风险",
        explanation="合同约定乙方/卖方承担卸车过程中的货物损毁灭失风险，触发风险",
        risk_exclusion="合同无乙方/卖方承担卸车过程中货物损毁灭失风险的相关表述",
    ),
    RuleCreate(
        risk_element="履约交付平台 - 乙方承担监造监制费用",
        explanation="合同约定监造/监制费用由乙方/卖方承担，触发风险",
        risk_exclusion="合同约定监造/监制费用不由乙方/卖方承担",
    ),
    RuleCreate(
        risk_element="履约交付平台 - 乙方承担直接安装调试义务",
        explanation="合同文本中存在乙方/卖方直接安装调试的相关描述，触发风险",
        risk_exclusion="合同仅约定乙方/卖方指导安装调试，无直接安装调试义务的相关表述",
    ),
    RuleCreate(
        risk_element="履约交付平台 - 质保期条款开口",
        explanation="合同质保期无明确固定期限，存在不闭口约定，触发风险",
        risk_exclusion="合同质保期有明确固定期限，条款完全闭口",
    ),
    RuleCreate(
        risk_element="履约交付平台 - 合同大小写金额不一致",
        explanation="合同文本中约定的大小写金额表述不一致，触发风险",
        risk_exclusion="合同文本中约定的大小写金额表述完全一致",
    ),
    RuleCreate(
        risk_element="知识产权部 - 知识产权归属甲方约定",
        explanation="合同约定新产生的知识产权或与产品相关的知识产权归买方/甲方所有，触发风险",
        risk_exclusion="合同知识产权归属约定符合公司标准要求，不归买方/甲方所有",
    ),
    RuleCreate(
        risk_element="知识产权部 - 全球知识产权不侵权责任约定",
        explanation="合同约定乙方承担全球范围内的知识产权不侵权责任，触发风险",
        risk_exclusion="合同无乙方承担全球范围内知识产权不侵权责任的相关约定",
    ),
    RuleCreate(
        risk_element="知识产权部 - 授权地域为全球范围",
        explanation="合同约定知识产权授予地域范围为全球范围内，触发风险",
        risk_exclusion="合同约定知识产权授权地域范围非全球范围",
    ),
    RuleCreate(
        risk_element="知识产权部 - 授权属性为可转让",
        explanation="合同约定知识产权授权属性为可转让的，触发风险",
        risk_exclusion="合同约定知识产权授权属性为不可转让",
    ),
    RuleCreate(
        risk_element="知识产权部 - 授权范围含生产制造",
        explanation="合同约定知识产权授权行为范围涉及生产制造，触发风险",
        risk_exclusion="合同约定知识产权授权行为范围不含生产制造",
    ),
    RuleCreate(
        risk_element="财务部 - 合同无不含税价格约定",
        explanation="合同文本中未标注不含税价格/不含税金额，触发风险",
        risk_exclusion="合同文本已明确标注不含税价格/不含税金额",
    ),
    RuleCreate(
        risk_element="财务部 - 税率计价规则约定不规范",
        explanation="合同未约定以不含税价格/金额为准，或未约定合同执行期间相关法律调整税率时按现行税率规定执行，触发风险",
        risk_exclusion="合同已约定以不含税价格/金额为准，或已约定税率调整时按现行税率规定执行",
    ),
    RuleCreate(
        risk_element="财务部 - 逾期付款违约责任缺失",
        explanation="合同未约定逾期付款、未按合同约定时间支付货款、未按约定付款方式支付货款的违约责任，触发风险",
        risk_exclusion="合同已明确约定逾期付款、未按约定时间/方式付款的违约责任",
    ),
    RuleCreate(
        risk_element="财务部 - 付款方式超出合规范围",
        explanation="合同约定付款方式为电汇、《2025 银行承兑汇票接收名单内》银行出具的银行承兑汇票以外的方式，触发风险",
        risk_exclusion="合同约定付款方式为电汇、《2025 银行承兑汇票接收名单内》银行出具的银行承兑汇票",
    ),
    RuleCreate(
        risk_element="财务部 - 付款方式不符合指定类型",
        explanation="合同约定付款方式不是银行转账、电汇、6个月内银行承兑汇票其中之一，触发风险",
        risk_exclusion="合同约定付款方式为银行转账、电汇、6个月内银行承兑汇票其中之一",
    ),
    RuleCreate(
        risk_element="财务部 - 约定背靠背付款条款",
        explanation="合同约定以业主向甲方支付对应款项为甲方付款前提的背靠背付款方式，触发风险",
        risk_exclusion="合同无任何背靠背付款相关约定",
    ),
    RuleCreate(
        risk_element="财务部 - 乙方承担二次运输费用",
        explanation="合同约定变更送达地产生的二次运输费由乙方/卖方承担，触发风险",
        risk_exclusion="合同无乙方/卖方承担二次运输费的相关约定",
    ),
    RuleCreate(
        risk_element="财务部 - 乙方承担到货后装卸费",
        explanation="合同约定到货后的装卸费由乙方/卖方承担，触发风险",
        risk_exclusion="合同无乙方/卖方承担到货后装卸费的相关约定",
    ),
    RuleCreate(
        risk_element="财务部 - 乙方负责卸货义务",
        explanation="合同约定乙方/卖方负责卸货，触发风险",
        risk_exclusion="合同无乙方/卖方负责卸货的相关约定",
    ),
    RuleCreate(
        risk_element="财务部 - 违约金票据义务未约定",
        explanation="合同未约定违约、违约金、违约处罚相关款项需提供对应票据，触发风险",
        risk_exclusion="合同已明确约定违约、违约金、违约处罚相关款项需提供合规票据",
    ),
    RuleCreate(
        risk_element="财务部 - 合同涉及红旗国家/地区",
        explanation="合同涉及俄罗斯、伊朗、朝鲜、古巴、叙利亚、克里米亚、塞瓦斯托波尔（克里米亚）、顿涅茨克州、卢甘斯克州、赫尔松州、扎波罗热州任一国家/地区，触发风险",
        risk_exclusion="合同不涉及上述红旗国家/地区",
    ),
    RuleCreate(
        risk_element="信用与应收账款平台 - 支付方式为商业汇票",
        explanation="合同约定支付方式为商票/商业汇票，触发风险",
        risk_exclusion="合同约定支付方式非商票/商业汇票",
    ),
    RuleCreate(
        risk_element="信用与应收账款平台 - 约定背靠背付款条款",
        explanation="合同约定以业主/总包方付款为前提、等比例支付、业主迟延付款可顺延付款的背靠背付款条款，触发风险",
        risk_exclusion="合同无任何背靠背付款、等比例支付、业主原因顺延付款的相关约定",
    ),
    RuleCreate(
        risk_element="信用与应收账款平台 - 约定款项顺延支付条款",
        explanation="合同约定质保期/款项支付可因质量问题处置后顺延支付，触发风险",
        risk_exclusion="合同无任何款项顺延支付的相关约定",
    ),
    RuleCreate(
        risk_element="信用与应收账款平台 - 小额合同未约定全款提货",
        explanation="合同总金额＜50万元，且未约定全款提货条款，触发风险",
        risk_exclusion="合同总金额≥50万元，或总金额＜50万元且已明确约定全款提货条款",
    ),
    RuleCreate(
        risk_element="法务部 - 付款条件条款开口",
        explanation="合同付款约定存在开口表述，如产品到货后/验收后/质保期满后支付货款、卖方提交材料经买方审核后支付货款，无明确付款期限，触发风险",
        risk_exclusion="合同付款节点、付款条件、付款期限均明确闭口，无模糊开口表述",
    ),
    RuleCreate(
        risk_element="法务部 - 约定背靠背付款及免责条款",
        explanation="合同约定买方付款以收到业主对应款项为前提、卖方承诺不以买方延迟付款为由追究违约责任、卖方同意业主原因导致付款延迟不追究买方违约责任，触发风险",
        risk_exclusion="合同无背靠背付款前提、无买方延迟付款免责的相关约定",
    ),
    RuleCreate(
        risk_element="法务部 - 违约责任范围过高",
        explanation="合同违约责任约定中存在一切损失、全部损失、间接损失、经济损失、发电损失等扩大化表述，触发风险",
        risk_exclusion="合同违约责任仅限直接损失，无上述扩大化损失赔偿表述",
    ),
    RuleCreate(
        risk_element="法务部 - 无责任上限约定",
        explanation='合同未约定"卖方在本合同项下承担的责任上限为合同金额 xx%"的责任限制条款，触发风险',
        risk_exclusion="合同已明确约定卖方在本合同项下承担的责任上限不超过合同金额约定比例",
    ),
    RuleCreate(
        risk_element="法务部 - 争议解决条款不规范",
        explanation="合同出现以下任一情形触发风险：1.同时约定可选择仲裁或诉讼两种争议解决方式；2.仲裁条款未明确具体的仲裁委员会；3.约定向卖方所在地有管辖权以外的法院提起诉讼；4.约定向上海仲裁委员会、北海仲裁委员会以外的仲裁机构提起仲裁",
        risk_exclusion="合同争议解决方式明确唯一，约定向买方所在地有管辖权的人民法院提起诉讼，或约定向上海仲裁委员会/北海仲裁委员会提起仲裁，机构全称明确",
    ),
    RuleCreate(
        risk_element="法务部 - 验收期限与标准约定缺失",
        explanation="合同未约定开箱检验期限、初步验收期限、最终验收期限、验收标准任一内容，触发风险",
        risk_exclusion="合同已明确约定开箱验收、初步验收、最终验收需在xx日内完成，并约定了明确的验收标准",
    ),
    RuleCreate(
        risk_element="法务部 - 不可抗力处理约定缺失",
        explanation="合同未明确不可抗力发生时的处理方案及处置期限，触发风险",
        risk_exclusion="合同已明确约定不可抗力发生后的处理方案、处置流程及对应期限",
    ),
    RuleCreate(
        risk_element="法务部 - 交货地点约定不明确",
        explanation="合同交货地点缺失、约定模糊不具体，触发风险",
        risk_exclusion="合同交货地点具体、明确、可落地执行",
    ),
    RuleCreate(
        risk_element="法务部 - 所有权转移约定超规",
        explanation='合同约定所有权转移节点超出"交付之日起转移"的标准，触发风险',
        risk_exclusion="合同约定标的物所有权自交付之日起转移",
    ),
    RuleCreate(
        risk_element="法务部 - 风险转移约定超规",
        explanation="超出标准：完成产品交货后，产品所有损害、丢失、毁损的风险转移至买方。触发风险",
        risk_exclusion="",
    ),
    RuleCreate(
        risk_element="质量管理部 - 质量责任范围扩大化",
        explanation="合同约定乙方承担质量问题引起的所有损失，而非仅直接损失，触发风险",
        risk_exclusion="合同约定乙方仅承担质量问题引起的直接损失，无扩大化责任表述",
    ),
]
