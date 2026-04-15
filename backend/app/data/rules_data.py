"""内置审核规则数据 — 方案B：按部门模块组织，区分 identify / judge / verify"""
from typing import Optional

from app.models.schemas import RuleCreate

# 全部模块名称（有序）
MODULES = [
    "履约交付平台",
    "知识产权部",
    "财务部",
    "合规部",
    "信用与应收账款平台",
    "法务部",
    "质量管理部",
]

BUILTIN_RULES: list[RuleCreate] = [
    # ======================================================================
    # 〇、跨模块共享规则
    # ======================================================================
    RuleCreate(
        rule_id="CMN-01",
        module="履约交付平台",
        shared_modules=["财务部", "法务部"],
        review_point="金额核对",
        review_type="verify",
        extraction_instruction=(
            "1. 提取标的物单价、数量、金额（分项明细，文本或表格形式，位于正文或附件清单）。\n"
            "2. 提取税率、税金。\n"
            "3. 提取合同总价（含税总价、不含税总价）。\n"
            "4. 提取大写金额与小写金额。"
        ),
        risk_criteria=(
            "1. 单价 × 数量 ≠ 分项金额 → 有风险。\n"
            "2. 分项金额合计 ≠ 合同总金额 → 有风险。\n"
            "3. 不含税金额 + 税金 ≠ 含税金额 → 有风险。\n"
            "4. 大写金额与小写金额不一致 → 有风险。\n"
            "5. 价税基本信息（单价/数量/金额/税率/税金/总价）缺失 → 有风险。"
        ),
    ),

    # ======================================================================
    # 一、履约交付平台（11 条）
    # ======================================================================
    RuleCreate(
        rule_id="LD-01",
        module="履约交付平台",
        review_point="交货周期",
        review_type="judge",
        extraction_instruction=(
            "1. 提取标的物产品名称、产品型号、数量。\n"
            "2. 提取合同约定的交货期/交货天数（到货期、交付日期都是交货期），识别交货起算条件：\n"
            "   - 合同生效后\n"
            "   - 卖方收到预付款和交货款后\n"
            "   - 双方对技术规范确认后\n"
            "   - 双方技术确认图纸及签订合同后"
        ),
        risk_criteria=(
            "合同约定交货天数 < 产品标准生产周期（需参照《产品生产周期统计汇总表》）。"
            "判定逻辑：提取合同交货天数 → 对照产品型号的标准周期 → 若小于则标记为风险。"
        ),
        notes="需外部数据：《产品生产周期统计汇总表》，当前阶段标注 needs_manual_review",
    ),
    RuleCreate(
        rule_id="LD-02",
        module="履约交付平台",
        review_point="包装",
        review_type="identify",
        extraction_instruction=(
            "提取以下信息：\n"
            "1. 是否约定包装标准？\n"
            "2. 是否约定包装物回收？\n"
            "3. 是否约定防潮、防湿、防震、防锈等运输保护？\n"
            "4. 是否有特殊要求（出口、环保、森林法相关）？"
        ),
    ),
    RuleCreate(
        rule_id="LD-03",
        module="履约交付平台",
        review_point="运输方式",
        review_type="judge",
        extraction_instruction=("识别合同是否约定的运输方式：公路运输 / 铁路运输 / 水路运输 / 航空运输等，若有约定，约定的运输方式是什么。如未约定，标注「未约定」。"),
         risk_criteria="航空运输→有风险。" ,
    ),
    RuleCreate(
        rule_id="LD-04",
        module="履约交付平台",
        review_point="交货方式",
        review_type="judge",
        extraction_instruction=(
            "1. 提取交货地址、联系人和联系方式。\n"
            "2. 提取是否约定「车板交货」。\n"
            "3. 提取是否约定「主变基础交货」或「主变基础就位」。\n"
            "4. 提取卸货承担方（甲方/买方 vs 乙方/卖方，含/不含/承担/不承担卸货）。"
        ),
        risk_criteria=(
            "风险条件（满足任一即判定为风险）：\n"
            "1. 未约定车板交货、主变基础交货、主变基础就位中的任何一个。\n"
            "2. 乙方/卖方承担卸货。"
        ),
    ),
    RuleCreate(
        rule_id="LD-05",
        module="履约交付平台",
        review_point="运费承担方",
        review_type="identify",
        extraction_instruction="识别运费承担方（甲方/买方 vs 乙方/卖方）。",
    ),
    RuleCreate(
        rule_id="LD-06",
        module="履约交付平台",
        review_point="监造",
        review_type="judge",
        extraction_instruction=(
            "1. 提取是否约定监造/监制。\n"
            "2. 提取监造/监制费用承担方。"
        ),
        risk_criteria="监造费用由乙方/卖方承担 → 有风险。甲方承担或未约定费用承担方 → 无风险。",
    ),
    RuleCreate(
        rule_id="LD-07",
        module="履约交付平台",
        review_point="运行",
        review_type="judge",
        extraction_instruction="提取是否约定乙方/卖方「指导安装调试」或「安装调试」。",
        risk_criteria=(
            "约定乙方/卖方安装调试（无「指导」前缀）→ 有风险。\n"
            "约定乙方/卖方「指导」安装调试 → 无风险。\n"
            "未作约定 → 无风险。\n"
            "关键区分：必须有「指导」二字才是无风险。"
        ),
    ),
    RuleCreate(
        rule_id="LD-08",
        module="履约交付平台",
        review_point="质保期-时长",
        review_type="judge",
        extraction_instruction=(
            "提取质保期时长及起算方式。起算方式包括：\n"
            "- 出厂后 / 货到现场 / 货到指定地点 / 货到项目地 / 货到买方现场 / 货到甲方现场 / 货到指定港口\n"
            "标准：≤12个月或18个月（二者以先到为准）。"
        ),
        risk_criteria="质保期 > 标准时长 → 有风险。",
    ),
    RuleCreate(
        rule_id="LD-08a",
        module="履约交付平台",
        review_point="质保期-低压",
        review_type="judge",
        applies_to="低压",
        extraction_instruction="提取质保期，标准为产品生产日期起的24个月或36个月内实行三包。",
        risk_criteria="超出标准（需按产品类别判断，参照《正泰电器产品质保期规定》）→ 有风险。",
        notes="需外部数据：《正泰电器产品质保期规定》",
    ),
    RuleCreate(
        rule_id="LD-08b",
        module="履约交付平台",
        review_point="质保期-诺雅克",
        review_type="judge",
        applies_to="诺雅克",
        extraction_instruction=(
            "提取质保期。\n"
            "标准：交货之日起18个月内或自产品验收合格之日起24个月（二者以晚到为准）。"
        ),
        risk_criteria="超出标准 → 有风险。",
    ),
    RuleCreate(
        rule_id="LD-09",
        module="履约交付平台",
        review_point="质保期-是否闭口",
        review_type="judge",
        extraction_instruction=(
            "判断质保期起算是否为「闭口」条件：\n"
            "- 闭口：出厂后、货到现场、货到指定地点、货到项目地、货到买方现场、货到甲方现场、货到指定港口、到货开箱验收。\n"
            "- 不闭口：设备验收合格后正常运行、工程移交生产验收报告签发之日起、签发初步验收证书之日、并网投入正常使用之日起、通过240h并网验收之日起、货到设备安装调试合格后、工程整体竣工后等。"
        ),
        risk_criteria=(
            "质保期起算条件为「不闭口」 → 有风险。\n"
            "关键区分：\n"
            "- 「货到现场」是闭口，「验收合格」是不闭口，「货到现场验收合格」是不闭口。\n"
            "- 「开箱验收」是闭口。"
        ),
    ),
    # ======================================================================
    # 二、知识产权部（3 条）
    # ======================================================================
    RuleCreate(
        rule_id="IP-01",
        module="知识产权部",
        review_point="知识产权归属",
        review_type="judge",
        extraction_instruction="提取合同中关于知识产权归属的约定。",
        risk_criteria="约定产生的新的知识产权或与产品相关的知识产权归买方所有 → 有风险。知识产权不得归属对方。",
    ),
    RuleCreate(
        rule_id="IP-02",
        module="知识产权部",
        review_point="知识产权不侵权保证",
        review_type="judge",
        extraction_instruction=(
            "1. 提取知识产权不侵权责任的地域范围。\n"
            "2. 提取是否承担经营损失的间接责任。\n"
            "3. 提取因此承担的违约责任金额或比例。"
        ),
        risk_criteria=(
            "满足任一即有风险：\n"
            "1. 承担全球范围的知识产权不侵权责任（应限定为交付地所在国）。\n"
            "2. 承担经营损失等间接损失。\n"
            "3. 违约金 > 合同总金额的5%或10万元（取最低）。"
        ),
    ),
    RuleCreate(
        rule_id="IP-03",
        module="知识产权部",
        review_point="知识产权授权",
        review_type="judge",
        extraction_instruction=(
            "1. 提取授权地域范围。\n"
            "2. 提取授权属性（是否可转让）。\n"
            "3. 提取授权行为范围（是否涉及生产制造）。"
        ),
        risk_criteria=(
            "满足任一即有风险：\n"
            "1. 授权地域范围为全球（应限定为交付地所在国）。\n"
            "2. 授权属性为可转让（应为不可转让）。\n"
            "3. 授权行为涉及生产制造（不应涉及）。"
        ),
    ),

    # ======================================================================
    # 三、财务部（8 条 + 共享 CMN-01）
    # ======================================================================
    RuleCreate(
        rule_id="FN-01",
        module="财务部",
        review_point="税率约定",
        review_type="judge",
        extraction_instruction=(
            "1. 提取不含税价格/金额及税额。\n"
            "2. 提取是否约定以不含税价格为准或按现行税率规定执行。\n"
            "3. 提取税率，区分设备类/工程类/服务类。"
        ),
        risk_criteria=(
            "1. 无不含税价格/金额 → 有风险。\n"
            "2. 未约定税率调整条款 → 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="FN-02",
        module="财务部",
        review_point="逾期付款违约条款",
        review_type="judge",
        extraction_instruction="提取是否有逾期付款违约/未按约定时间付款/未按约定方式付款的条款。",
        risk_criteria="未约定逾期付款违约条款 → 有风险。",
        notes="建议：按照同期银行贷款利息收取资金占用费。",
    ),
    RuleCreate(
        rule_id="FN-03",
        module="财务部",
        review_point="付款方式-诺雅克",
        review_type="judge",
        applies_to="诺雅克",
        extraction_instruction=(
            "1. 提取付款方式。\n"
            "2. 判断是否属于电汇或银行承兑汇票。"
        ),
        risk_criteria="除电汇/银行承兑汇票（须在《2025银行承兑汇票接收名单》内）以外的付款方式 → 有风险。",
        notes="需外部数据：《2025银行承兑汇票接收名单》",
    ),
    RuleCreate(
        rule_id="FN-03a",
        module="财务部",
        review_point="付款方式-输配电",
        review_type="judge",
        applies_to="输配电",
        extraction_instruction=(
            "1. 提取付款方式。\n"
            "2. 判断是否属于银行转账、电汇、6个月内银行承兑汇票。"
        ),
        risk_criteria=(
            "1. 除银行转账/电汇/6个月内银行承兑汇票以外的付款方式 → 有风险。\n"
            "2. 背靠背付款方式 → 重大风险。"
        ),
    ),
    RuleCreate(
        rule_id="FN-04",
        module="财务部",
        review_point="质保金",
        review_type="judge",
        extraction_instruction="提取质保金比例。",
        risk_criteria=(
            "诺雅克：质保金 > 3%-5% → 有风险。\n"
            "输配电：质保金 > 10% → 有风险。"
        ),
        notes="适用诺雅克和输配电",
    ),
    RuleCreate(
        rule_id="FN-05",
        module="财务部",
        review_point="运输费用",
        review_type="judge",
        extraction_instruction=(
            "1. 提取是否约定变更送达地或二次运输费的承担方。\n"
            "2. 提取卸货费用承担方。"
        ),
        risk_criteria=(
            "1. 变更送达地或二次运输费由乙方/卖方承担 → 有风险。\n"
            "2. 到货后装卸费由乙方/卖方承担 → 有风险。\n"
            "3. 乙方/卖方负责卸货 → 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="FN-06",
        module="财务部",
        review_point="发票",
        review_type="judge",
        extraction_instruction=(
            "1. 识别合同约定的发票类型：增值税普通发票/增值税专用发票。\n"
            "2. 识别是否约定违约/违约金/违约处罚需提供票据。"
        ),
        risk_criteria="未约定违约/违约金/违约处罚提供票据 → 有风险。发票类型仅识别，不判定风险。",
    ),
    RuleCreate(
        rule_id="FN-08",
        module="财务部",
        review_point="保函",
        review_type="identify",
        extraction_instruction=(
            "1. 提取是否约定履约保函、预付款保函、质量保函等。\n"
            "2. 提取保函时间要求。\n"
            "3. 提取保函格式要求（银行格式/特定格式）。"
        ),
    ),

    # ======================================================================
    # 四、合规部（4 条）
    # ======================================================================
    RuleCreate(
        rule_id="CP-01",
        module="合规部",
        review_point="客户风险",
        review_type="identify",
        extraction_instruction=(
            "本评审点需通过外部平台（道琼斯、邓白氏、OFAC、天眼查）核查客户信息。\n"
            "LLM仅提示：需人工核验客户是否存在制裁记录、不当行为、负面报道、失信被执行、破产等。"
        ),
        notes="需外部系统支持，标注 needs_manual_review",
    ),
    RuleCreate(
        rule_id="CP-02",
        module="合规部",
        review_point="合规条款审核",
        review_type="judge",
        extraction_instruction=(
            "重点搜索合同中「合规条款」章节，识别以下条款的存在及内容：\n"
            "- 审计条款（检查权、审计权、账簿审查、合规审查、监督审计）\n"
            "- 廉洁条款（反腐败、廉政承诺、反贿赂、禁止不当支付）\n"
            "- 数据合规条款（GDPR、个人信息保护、数据隐私、数据安全、跨境传输）\n"
            "- 反强迫劳动条款（现代奴隶制、供应链劳工、冲突矿物）\n"
            "- 人权保护条款（社会责任、ESG、ILO标准）\n"
            "- 反垄断/公平竞争条款\n"
            "- 制裁条款（国际制裁合规、禁运、受限制方清单）\n"
            "- 出口管制条款（贸易合规、美国出口管制、技术管制、跨境转移限制）\n"
            "- 反洗钱条款\n"
            "- 利益冲突条款（关联交易披露、回避）\n"
            "识别合规条款的违约责任是否过重。"
        ),
        risk_criteria=(
            "1. 条款违背正泰诚信合规要求（参考《正泰集团诚信合规商业行为准则》） → 有风险。\n"
            "2. 合规条款违约责任过重 → 有风险。\n"
            "3. 存在审计条款 → 需提示。"
        ),
         notes="需人工与《正泰集团诚信合规商业行为准则》进行核对，标注 needs_manual_review",
    ),
    RuleCreate(
        rule_id="CP-03",
        module="合规部",
        review_point="项目涉及国家",
        review_type="judge",
        extraction_instruction=(
            "1. 识别合同是否涉及对外转卖、转运、转让、分销、经销、二次销售。\n"
            "2. 识别合同涉及的交货国家/地区。"
        ),
        risk_criteria=(
            "涉及以下红旗国 → 有风险：\n"
            "俄罗斯、伊朗、朝鲜、古巴、叙利亚、克里米亚、塞瓦斯托波尔、"
            "顿涅茨克州、卢甘斯克州、赫尔松州、扎波罗热州。"
        ),
    ),
    RuleCreate(
        rule_id="CP-04",
        module="合规部",
        review_point="是否存在代理",
        review_type="judge",
        extraction_instruction=(
            "1. 识别合同是否涉及代理商。\n"
            "2. 识别代理佣金比例。"
        ),
        risk_criteria=(
            "1. 涉及代理但未签署完整合规文件 → 有风险。\n"
            "2. 代理佣金 > 5% → 有风险。"
        ),
        notes="代理佣金信息可能在OA流程中而非合同文本中，如合同中未找到则标注「需人工核验」。",
    ),

    # ======================================================================
    # 五、信用与应收账款平台（4 条）
    # ======================================================================
    RuleCreate(
        rule_id="CR-01",
        module="信用与应收账款平台",
        review_point="客户风险",
        review_type="identify",
        extraction_instruction=(
            "本评审点需通过外部系统（天眼查、SAP、信控平台、公司法务诉讼记录）核验。\n"
            "LLM仅提示需人工核验：\n"
            "1. 客户是否被列为失信被执行人、限制高消费、有破产/合同纠纷案件。\n"
            "2. 客户是否已被公司起诉。\n"
            "3. 客户应收账款是否逾期超6个月。\n"
            "4. 私人企业实缴资本是否 < 3000万元。\n"
            "5. 客户股权是否被冻结。"
        ),
        notes="需外部系统支持，标注 needs_manual_review",
    ),
    RuleCreate(
        rule_id="CR-02",
        module="信用与应收账款平台",
        review_point="付款条款",
        review_type="judge",
        extraction_instruction=(
            "1. 提取支付方式（银行转账/电汇/承兑/商票/平台）。\n"
            "2. 提取付款节点是否闭口（如「到货后**内」「发货后**内」为闭口；含验收合格、试运行合格等为开口）。\n"
            "3. 提取是否有「顺延支付」等违约条款。"
        ),
        risk_criteria=(
            "1. 商票/商业汇票 → 有风险。\n"
            "2. 背靠背付款方式 → 重大风险（需特别提示）。\n"
            "3. 约定「顺延支付」 → 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="CR-03",
        module="信用与应收账款平台",
        review_point="付款账期",
        review_type="judge",
        extraction_instruction=(
            "提取付款账期天数。\n"
            "- 行业业务：对照《行业销售货款回笼与应收管控》。\n"
            "- 渠道业务：对照《分销业务信用支持与应收管控》，盘厂/OEM/建筑楼宇≤90天。"
        ),
        risk_criteria="超出标准账期 → 有风险。需人工参照具体管控文件确认。",
        notes="需外部数据：管控文件标准",
    ),
    RuleCreate(
        rule_id="CR-04",
        module="信用与应收账款平台",
        review_point="付款比例",
        review_type="judge",
        extraction_instruction=(
            "1. 提取各付款节点及比例。\n"
            "2. 判断合同金额是否 < 50万元。"
        ),
        risk_criteria=(
            "1. 付款比例超出《行业销售货款回笼与应收管控》标准 → 有风险。\n"
            "2. 合同金额 < 50万元且未约定全款提货 → 有风险。"
        ),
        risk_exclusion="豁免条件：信用免评客户、集团内产业公司业务、主合同增补合同、框架中标的分批次订单。",
    ),

    # ======================================================================
    # 六、法务部（12 条 + 共享 CMN-01）
    # ======================================================================
    RuleCreate(
        rule_id="LG-01",
        module="法务部",
        review_point="付款条款",
        review_type="judge",
        extraction_instruction=(
            "1. 提取买方付款节点及条件是否明确。\n"
            "2. 识别是否存在背靠背付款约定。"
        ),
        risk_criteria=(
            "1. 付款条件为开口（如「审核后支付」「验收后支付」而无明确天数）→ 有风险。\n"
            "2. 背靠背付款条件（如「收到业主款项后支付」「不以延迟付款追究违约」）→ 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="LG-02",
        module="法务部",
        review_point="违约责任",
        review_type="judge",
        extraction_instruction=(
            "1. 提取违约金计算依据及数额。\n"
            "2. 提取是否约定卖方违约责任上限。"
        ),
        risk_criteria=(
            "1. 违约责任包含「一切损失」「全部损失」「间接损失」「发电损失」等宽泛表述 → 有风险。\n"
            "2. 合同中未约定责任限制条件（如「卖方在本合同项下承担的责任上限为合同金额【】%」）→ 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="LG-03",
        module="法务部",
        review_point="违约金-输配电诺雅克",
        review_type="judge",
        applies_to="输配电",
        extraction_instruction="提取违约金金额或比例。",
        risk_criteria="违约金 > 合同总额5% → 有风险。",
        notes="同样适用于诺雅克",
    ),
    RuleCreate(
        rule_id="LG-03a",
        module="法务部",
        review_point="违约金-低压",
        review_type="judge",
        applies_to="低压",
        extraction_instruction="提取违约金金额或比例。",
        risk_criteria="违约金 > 合同总额30% → 有风险。",
    ),
    RuleCreate(
        rule_id="LG-04",
        module="法务部",
        review_point="管辖",
        review_type="judge",
        extraction_instruction=(
            "1. 提取争议解决方式（仲裁/诉讼）。\n"
            "2. 提取仲裁委员会名称或管辖法院。"
        ),
        risk_criteria=(
            "1. 仲裁条款无效（可仲裁可诉讼选其一/未明确具体仲裁委）→ 有风险。\n"
            "2. 管辖机构对卖方不利：除上海仲裁委员会和北海仲裁委员会以外的仲裁 → 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="LG-05",
        module="法务部",
        review_point="验收",
        review_type="judge",
        extraction_instruction=(
            "识别合同是否约定开箱验收、初步验收、最终验收。\n"
            "提取各验收节点的期限（「在【】日内完成」）和验收标准。\n"
            "提取「未按约履行视为验收合格」的默认条款。"
        ),
        risk_criteria="未约定验收期限或验收标准 → 有风险。",
    ),
    RuleCreate(
        rule_id="LG-07",
        module="法务部",
        review_point="不可抗力",
        review_type="judge",
        extraction_instruction="提取不可抗力条款的处理方案及期限。",
        risk_criteria=(
            "1. 不可抗力约定损害卖方权益 → 有风险。\n"
            "2. 未明确处理方案及期限 → 有风险。"
        ),
    ),
    RuleCreate(
        rule_id="LG-08",
        module="法务部",
        review_point="客户注册资本",
        review_type="identify",
        extraction_instruction=(
            "本评审点需外部数据支持。\n"
            "LLM仅提示：需人工核验客户注册资本和实缴资本是否 ≥ 合同金额。"
        ),
        notes="需外部数据：天眼查，标注 needs_manual_review",
    ),
    RuleCreate(
        rule_id="LG-09",
        module="法务部",
        review_point="交货地点",
        review_type="judge",
        extraction_instruction="提取交货地点是否明确具体（*省*市*区*路*号）。",
        risk_criteria="交货地点缺失或不明确（如仅写「项目现场」）→ 有风险。",
    ),
    RuleCreate(
        rule_id="LG-10",
        module="法务部",
        review_point="所有权条款",
        review_type="judge",
        extraction_instruction="提取关于货物所有权的约定。",
        risk_criteria="交付之日起即转移所有权（标准应为：买方付清合同总价前卖方保留所有权）→ 有风险。",
    ),
    RuleCreate(
        rule_id="LG-11",
        module="法务部",
        review_point="风险转移",
        review_type="judge",
        extraction_instruction="提取关于货物风险转移的约定。",
        risk_criteria="产品验收之前的风险由卖方承担（标准应为：完成交货后风险转移至买方）→ 有风险。",
    ),
    RuleCreate(
        rule_id="LG-12",
        module="法务部",
        review_point="附件核对",
        review_type="verify",
        extraction_instruction=(
            "1. 提取合同正文中提到但未提供全文的附件序号和名称。\n"
            "2. 核对下文实际提供全文的附件是否齐全、序号是否一致。"
        ),
        risk_criteria="正文引用与实际附件不一致或附件不齐全 → 有风险。",
    ),

    # ======================================================================
    # 七、质量管理部（4 条）
    # ======================================================================
    RuleCreate(
        rule_id="QM-01",
        module="质量管理部",
        review_point="技术协议整理",
        review_type="identify",
        extraction_instruction=(
            "将技术协议的全部内容整理成结构化表格形式，便于审核和查阅。\n"
            "包括：技术参数、性能指标、试验要求、检验标准等。"
        ),
    ),
    RuleCreate(
        rule_id="QM-02",
        module="质量管理部",
        review_point="变更管理",
        review_type="judge",
        extraction_instruction="提取是否约定所有变更均须经客户确认方可实施。",
        risk_criteria="存在违规变更处罚或未约定变更须经客户确认 → 有风险。",
    ),
    RuleCreate(
        rule_id="QM-03",
        module="质量管理部",
        review_point="质量损失承担",
        review_type="judge",
        extraction_instruction="提取质量异常后的损失承担原则。",
        risk_criteria="承担因质量问题造成的间接损失/所有损失（标准为仅承担直接损失）→ 有风险。",
    ),
    RuleCreate(
        rule_id="QM-04",
        module="质量管理部",
        review_point="质量协议与处罚",
        review_type="identify",
        extraction_instruction=(
            "1. 识别国网相关的到货检验、送样试验不合格处罚条款（处罚金额、扣分、暂停中标资质等）。\n"
            "2. 识别行业客户质量协议中的：\n"
            "   - 产品合格率、批量失效率、DPPM、LAR、来料质量KPI等指标及处罚金额。\n"
            "   - 环保要求（RoHS、REACH、POPs）及处罚。\n"
            "   - PCN变更要求、物料安全、错混料等问题的处罚要求。\n"
            "   - 赔偿金额、处罚金额、「承担一切损失」等表述。\n"
            "识别后进行提示，由人工判断风险。"
        ),
    ),
]


def get_rules_by_module(
    module: str, company: Optional[str] = None
) -> list[RuleCreate]:
    """按模块 + 产业公司筛选规则。company=None 时返回所有通用规则及该模块全部规则。
    支持 shared_modules：规则的主模块或共享模块匹配即返回。"""
    results = []
    for r in BUILTIN_RULES:
        if r.module != module and module not in r.shared_modules:
            continue
        if r.applies_to is not None and company is not None and r.applies_to != company:
            continue
        if r.applies_to is not None and company is None:
            continue
        results.append(r)
    return results


def get_all_modules() -> list[str]:
    """返回所有模块名称（有序）"""
    return list(MODULES)
