#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件 11-30: B类数据 - 模板配置类数据
改造前: 硬编码文本和配置
改造后: JSON/YAML配置+Jinja2模板
"""

# ========== 文件 11: contract_templates.py (改造前) ==========
"""
# 改造前 - 硬编码合同模板
FUND_PURCHASE_AGREEMENT = """
基金购买协议

甲方（投资者）：_____________
乙方（基金管理人）：_____________

鉴于甲方愿意购买乙方管理的基金产品，双方本着平等自愿的原则，达成如下协议：

第一条 基金产品信息
基金名称：{fund_name}
基金代码：{fund_code}
基金类型：{fund_type}
风险等级：{risk_level}

第二条 购买金额
甲方同意以人民币 {amount} 元购买上述基金产品。

第三条 费用说明
申购费率：{purchase_fee}%
管理费率：{management_fee}%
托管费率：{custody_fee}%

第四条 风险提示
基金投资有风险，过往业绩不代表未来表现。甲方应充分了解基金风险后再做投资决定。

签署日期：{sign_date}
"""

FUND_RISK_DISCLOSURE = """
风险揭示书

尊敬的投资者：

感谢您选择购买{fund_name}基金。在您做出投资决策前，请仔细阅读以下内容：

1. 市场风险：基金投资受证券市场波动影响，可能面临本金损失风险。
2. 流动性风险：基金可能面临赎回困难或无法及时变现的风险。
3. 管理风险：基金管理人的管理能力可能影响基金业绩。
4. 政策风险：国家政策变化可能对基金投资产生影响。

本人已充分理解上述风险，自愿承担投资风险。

投资者签名：__________ 日期：__________
"""
"""

# ========== 文件 12: compliance_rules.py (改造前) ==========
"""
# 改造前 - 硬编码合规规则
COMPLIANCE_RULES = {
    "适当性匹配": {
        "保守型": ["货币基金", "债券基金", "同业存单基金"],
        "稳健型": ["货币基金", "债券基金", "混合基金", "FOF"],
        "平衡型": ["债券基金", "混合基金", "指数基金", "QDII"],
        "成长型": ["混合基金", "股票基金", "指数基金", "QDII", "商品基金"],
        "进取型": ["股票基金", "指数基金", "QDII", "商品基金", "REITs"]
    },
    "最低投资金额": {
        "公募基金": 1,
        "私募基金": 1000000,
        "专户产品": 100000,
        "资管计划": 300000
    },
    "冷静期": {
        "私募基金": 24,  # 小时
        "专户产品": 24,
        "资管计划": 24
    }
}

DISCLOSURE_REQUIREMENTS = [
    "基金合同生效公告",
    "基金招募说明书",
    "基金托管协议",
    "风险揭示书",
    "投资者权益须知",
    "产品资料概要"
]
"""

# ========== 文件 13: due_diligence_checklist.py (改造前) ==========
"""
# 改造前 - 硬编码尽调清单
DUE_DILIGENCE_ITEMS = [
    {"category": "基础信息", "items": [
        "基金管理人营业执照",
        "基金管理人业务资格证明",
        "基金管理人股权结构",
        "基金管理人组织架构",
        "基金管理人高管简历"
    ]},
    {"category": "投资管理", "items": [
        "投资管理制度",
        "投资决策流程",
        "风控管理制度",
        "合规管理制度",
        "关联交易管理制度"
    ]},
    {"category": "运营情况", "items": [
        "近三年管理规模",
        "近三年产品业绩",
        "客户结构分析",
        "费率结构说明",
        "销售渠道分布"
    ]},
    {"category": "合规情况", "items": [
        "监管处罚记录",
        "自律处分记录",
        "投诉处理情况",
        "法律诉讼情况",
        "合规报告"
    ]}
]

MANAGER_EVALUATION_CRITERIA = {
    "投资能力": {"weight": 0.40, "metrics": ["长期业绩", "超额收益", "风险控制"]},
    "风控能力": {"weight": 0.25, "metrics": ["回撤控制", "波动率管理", "极端情况应对"]},
    "合规情况": {"weight": 0.20, "metrics": ["处罚记录", "合规制度", "执行效果"]},
    "运营能力": {"weight": 0.15, "metrics": ["规模增长", "人员稳定", "系统支持"]}
}
"""

# ========== 文件 14: report_templates.py (改造前) ==========
"""
# 改造前 - 硬编码报告模板
MONTHLY_REPORT_TEMPLATE = """
{fund_name}月度运作报告
报告期间：{start_date} 至 {end_date}

一、基金概况
基金名称：{fund_name}
基金代码：{fund_code}
基金类型：{fund_type}
成立日期：{establish_date}
报告期末规模：{aum} 亿元

二、业绩表现
报告期内净值增长率：{period_return}%
业绩比较基准收益率：{benchmark_return}%
超额收益：{alpha}%

三、市场回顾
{market_review}

四、投资策略回顾
{strategy_review}

五、持仓分析
前十大重仓股：
{top_holdings}

六、后市展望
{outlook}

风险提示：基金过往业绩不代表未来表现，投资需谨慎。
"""

QUARTERLY_REPORT_TEMPLATE = """
{fund_name}季度报告
报告季度：{quarter}

一、重要提示
基金管理人承诺以诚实信用、勤勉尽责的原则管理和运用基金资产。

二、基金产品概况
{product_summary}

三、主要财务指标
{financial_indicators}

四、管理人报告
{manager_report}

五、投资组合报告
{portfolio_report}

六、开放式基金份额变动
{share_changes}

七、备查文件
{reference_files}
"""
"""

# ========== 文件 15: announcement_templates.py (改造前) ==========
"""
# 改造前 - 硬编码公告模板
FUND_MANAGER_CHANGE_NOTICE = """
关于{fund_name}基金经理变更的公告

公告日期：{announce_date}
公告编号：{announce_no}

一、基金经理变更情况
原基金经理：{former_manager}
新任基金经理：{new_manager}
变更原因：{change_reason}
生效日期：{effective_date}

二、新任基金经理简介
姓名：{manager_name}
学历：{education}
从业年限：{experience_years}年
过往履历：{career_history}
管理产品：{managed_products}

三、其他事项
本次变更已按规定向中国证监会及相关机构备案。

特此公告。

{company_name}
{announce_date}
"""

FUND_DIVIDEND_NOTICE = """
{fund_name}分红公告

公告编号：{announce_no}
权益登记日：{record_date}
除息日：{ex_date}
现金红利发放日：{payment_date}
分红方案：每10份基金份额派发红利 {dividend_per_share} 元

本次分红为基金第 {dividend_times} 次分红。

风险提示：分红并不意味着投资收益的保障。

{company_name}
{announce_date}
"""

FUND_MERGER_NOTICE = """
关于{fund_name}基金合并的公告

根据基金合同约定，{source_fund}将并入{target_fund}。

合并基准日：{merge_date}
合并比例：{merge_ratio}
份额转换方式：{conversion_method}

持有人权益保护：
{holder_protection}

{company_name}
{announce_date}
"""
"""

# ========== 文件 16: notification_templates.py (改造前) ==========
"""
# 改造前 - 硬编码通知模板
INVESTOR_NOTIFICATIONS = {
    "交易确认": """
尊敬的投资者：

您于 {trade_date} 提交的{trade_type}申请已确认。

基金名称：{fund_name}
基金代码：{fund_code}
确认份额：{confirmed_shares} 份
确认金额：{confirmed_amount} 元
确认净值：{nav} 元
手续费：{fee} 元

如有疑问，请联系客服热线：400-xxx-xxxx
""",
    
    "分红通知": """
尊敬的投资者：

您持有的{fund_name}将于{payment_date}进行分红。

分红方案：每10份派{dividend}元
您的持有份额：{shares}份
预计分红金额：{expected_dividend}元

分红方式：{dividend_method}

如有疑问，请联系客服热线：400-xxx-xxxx
""",
    
    "巨额赎回": """
尊敬的投资者：

您于 {trade_date} 提交的赎回申请因巨额赎回被部分确认。

申请份额：{applied_shares} 份
确认份额：{confirmed_shares} 份
未确认份额：{unconfirmed_shares} 份（将顺延至下一交易日处理）

如有疑问，请联系客服热线：400-xxx-xxxx
"""
}
"""

# ========== 文件 17: regulatory_articles.py (改造前) ==========
"""
# 改造前 - 硬编码法规条文
SECURITIES_LAW_ARTICLES = [
    {
        "law": "证券投资基金法",
        "article": "第七十一条",
        "content": "基金管理人、基金托管人应当按照基金合同的约定，向基金份额持有人提供基金信息。",
        "applicable_scenarios": ["信息披露", "投资者权益保护"]
    },
    {
        "law": "证券投资基金法",
        "article": "第七十五条",
        "content": "基金管理人应当妥善保存基金管理业务活动的记录、账册、报表和其他相关资料。",
        "applicable_scenarios": ["档案管理", "合规检查"]
    },
    {
        "law": "私募投资基金监督管理暂行办法",
        "article": "第十六条",
        "content": "私募基金管理人应当自行或者委托第三方机构对私募基金进行风险评级。",
        "applicable_scenarios": ["适当性管理", "风险评估"]
    },
    {
        "law": "证券期货投资者适当性管理办法",
        "article": "第二十二条",
        "content": "禁止向普通投资者主动推介风险等级高于其风险承受能力的产品或者服务。",
        "applicable_scenarios": ["销售合规", "适当性匹配"]
    }
]

SELF_REGULATORY_RULES = [
    {
        "organization": "中国证券投资基金业协会",
        "rule": "私募投资基金募集行为管理办法",
        "key_points": [
            "募集机构应当履行适当性义务",
            "禁止公开宣传",
            "设置投资冷静期",
            "回访确认制度"
        ]
    },
    {
        "organization": "中国证券投资基金业协会",
        "rule": "基金募集机构投资者适当性管理实施指引",
        "key_points": [
            "投资者分类",
            "产品分级",
            "适当性匹配",
            "风险揭示"
        ]
    }
]
"""

# ========== 文件 18: qa_templates.py (改造前) ==========
"""
# 改造前 - 硬编码问答模板
COMMON_QA = [
    {
        "question": "什么是基金的申购和赎回？",
        "answer": """申购是指投资者向基金公司购买基金份额的行为。
赎回是指投资者向基金公司卖出基金份额的行为。
申购和赎回的价格以申请当日的基金份额净值为准。""",
        "category": "基础知识"
    },
    {
        "question": "基金净值是什么意思？",
        "answer": """基金净值是指每份基金份额的资产净值。
计算公式：基金净值 = (基金总资产 - 基金总负债) / 基金总份额
基金净值每个交易日收盘后计算并公布。""",
        "category": "基础知识"
    },
    {
        "question": "什么是基金定投？",
        "answer": """基金定投是指投资者在固定的时间以固定的金额投资到指定的基金中。
优点：
1. 分散投资风险
2. 平均投资成本
3. 培养长期投资习惯
4. 自动扣款，省时省力""",
        "category": "投资策略"
    },
    {
        "question": "如何选择适合自己的基金？",
        "answer": """选择基金时应考虑以下因素：
1. 风险承受能力：评估自己的风险偏好
2. 投资目标：明确投资期限和收益预期
3. 基金类型：根据需求选择股票型、债券型或混合型
4. 历史业绩：关注长期业绩而非短期表现
5. 基金经理：了解基金经理的投资风格和经验""",
        "category": "投资指导"
    }
]

HOT_TOPIC_QA = [
    {
        "topic": "公募基金降费",
        "qa_pairs": [
            {
                "q": "公募基金降费对投资者有什么影响？",
                "a": "降费可以降低投资者的成本，提升长期投资收益。"
            },
            {
                "q": "哪些费用会下调？",
                "a": "主要包括管理费率、托管费率、交易佣金等。"
            }
        ]
    },
    {
        "topic": "ETF投资",
        "qa_pairs": [
            {
                "q": "什么是ETF？",
                "a": "ETF是交易所交易基金，可以在二级市场像股票一样买卖。"
            },
            {
                "q": "ETF有哪些优势？",
                "a": "成本低、透明度高、交易灵活、分散风险。"
            }
        ]
    }
]
"""

# ========== 文件 19: marketing_templates.py (改造前) ==========
"""
# 改造前 - 硬编码营销文案
PRODUCT_PROMOTION_TEMPLATES = {
    "新发基金": """
🎉 {fund_name} 火热发售中！

📊 产品亮点：
✨ {highlight_1}
✨ {highlight_2}
✨ {highlight_3}

👨‍💼 基金经理：{manager_name}
   {manager_introduction}

📅 认购时间：{subscription_start} 至 {subscription_end}
💰 认购起点：{min_amount}元

⚠️ 风险提示：基金有风险，投资需谨慎
""",

    "绩优基金": """
🏆 {fund_name} 业绩亮眼！

📈 业绩表现：
近一年：{return_1y}%
近三年：{return_3y}%
成立以来：{return_since_inception}%

⭐ 获得{award_name}奖项

📊 投资策略：{strategy}

🔥 限时申购费率{discount}折

⚠️ 风险提示：过往业绩不代表未来表现
""",

    "定投推广": """
💡 定投{fund_name}，分享长期收益

📅 每月只需{min_amount}元
🎯 坚持定投，复利效应
📊 历史回测数据显示：定投3年以上正收益概率{win_rate}%

🎁 新客专享：首次定投免申购费

⚠️ 风险提示：定投不能规避基金投资风险
"""
}
"""

# ========== 文件 20: training_materials.py (改造前) ==========
"""
# 改造前 - 硬编码培训材料
SALES_TRAINING_CONTENT = """
基金销售培训大纲

模块一：基金基础知识
1.1 基金的定义和特点
1.2 基金的分类
1.3 基金的费用结构
1.4 基金净值计算

模块二：监管法规
2.1 适当性管理办法
2.2 销售合规要求
2.3 禁止性行为
2.4 投资者权益保护

模块三：销售技巧
3.1 客户需求分析
3.2 产品匹配方法
3.3 异议处理技巧
3.4 售后服务要点

模块四：产品知识
4.1 权益类产品
4.2 固收类产品
4.3 混合型产品
4.4 指数型产品
4.5 QDII产品
"""

COMPLIANCE_TRAINING_CONTENT = """
合规培训要点

一、适当性管理
□ 了解客户：收集客户信息，评估风险承受能力
□ 了解产品：掌握产品特征、风险等级
□ 适当匹配：将合适的产品推荐给合适的客户

二、销售合规
□ 不得承诺收益
□ 不得夸大宣传
□ 不得误导投资者
□ 充分揭示风险

三、记录保存
□ 客户资料保存不少于20年
□ 交易记录保存不少于20年
□ 录音录像保存不少于20年
"""
"""

# 继续添加文件 21-30

# ========== 文件 21: review_checklists.py (改造前) ==========
"""
# 改造前 - 硬编码审查清单
FILING_MATERIAL_CHECKLIST = [
    {"item": "基金合同", "required": True, "review_points": ["条款完整性", "权利义务明确", "争议解决机制"]},
    {"item": "招募说明书", "required": True, "review_points": ["披露完整性", "风险提示充分", "业绩真实准确"]},
    {"item": "托管协议", "required": True, "review_points": ["托管人职责明确", "监督职责清晰"]},
    {"item": "法律意见书", "required": True, "review_points": ["出具机构资质", "意见明确", "依据充分"]},
    {"item": "验资报告", "required": True, "review_points": ["出具机构资质", "金额准确", "日期有效"]},
]

AD_HOC_ANNOUNCEMENT_CHECKLIST = [
    {"item": "公告标题", "check": "准确概括公告内容"},
    {"item": "公告编号", "check": "按年度连续编号"},
    {"item": "公告日期", "check": "与披露日期一致"},
    {"item": "正文内容", "check": "事实准确、表述清晰"},
    {"item": "附件", "check": "如有附件需完整上传"},
]
"""

# ========== 文件 22: disclosure_templates.py (改造前) ==========
"""
# 改造前 - 硬编码信息披露模板
MAJOR_EVENT_DISCLOSURE = """
{fund_name}重大事件临时报告

报告事由：{event_type}

一、事件概述
{event_summary}

二、事件影响分析
{impact_analysis}

三、应对措施
{measures}

四、其他事项
{other_matters}

基金管理人将按照法律法规和基金合同的规定，及时履行后续信息披露义务。

{company_name}
{report_date}
"""

PORTFOLIO_CHANGE_DISCLOSURE = """
关于{fund_name}投资范围变更的公告

根据基金合同约定和法律法规要求，本基金的投资范围将进行调整：

变更前：
{original_scope}

变更后：
{new_scope}

变更原因：{reason}
生效日期：{effective_date}

风险提示：投资范围变更可能对基金风险收益特征产生影响。

{company_name}
{announce_date}
"""
"""

# ========== 文件 23: meeting_templates.py (改造前) ==========
"""
# 改造前 - 硬编码会议纪要模板
INVESTMENT_COMMITTEE_MINUTES = """
投资决策委员会会议纪要

会议时间：{meeting_time}
会议地点：{meeting_location}
主持人：{chairperson}
出席人员：{attendees}
记录人：{recorder}

一、会议议题
{agenda}

二、讨论内容
{discussions}

三、决议事项
{resolutions}

四、后续行动
{action_items}

纪要整理：{recorder}
纪要日期：{minutes_date}
"""

RISK_COMMITTEE_MINUTES = """
风险控制委员会会议纪要

会议时间：{meeting_time}
出席人员：{attendees}

一、风险监控报告
{risk_report}

二、重大事项讨论
{major_issues}

三、风控措施
{risk_measures}

四、合规建议
{compliance_suggestions}
"""
"""

# ========== 文件 24: client_report_templates.py (改造前) ==========
"""
# 改造前 - 硬编码客户报告模板
CLIENT_PORTFOLIO_REPORT = """
尊敬的客户{client_name}：

以下是您的投资组合报告（报告期间：{start_date} 至 {end_date}）：

一、组合概览
总资产：{total_assets} 元
本期收益：{period_return} 元
收益率：{return_rate}%

二、持仓分布
{holding_distribution}

三、交易记录
{transaction_records}

四、业绩归因
{performance_attribution}

五、风险提示
{risk_warnings}

如需了解更多信息，请联系您的投资顾问。

{company_name}
{report_date}
"""

CLIENT_RISK_ASSESSMENT_REPORT = """
客户风险评估报告

客户姓名：{client_name}
评估日期：{assessment_date}

一、风险承受能力评估
评估结果：{risk_tolerance}
评估维度：
- 财务状况：{financial_status}
- 投资经验：{investment_experience}
- 风险偏好：{risk_preference}
- 投资期限：{investment_horizon}

二、适当性匹配建议
适合产品类型：{suitable_products}
不适合产品类型：{unsuitable_products}

三、投资建议
{investment_suggestions}
"""
"""

# ========== 文件 25: email_templates.py (改造前) ==========
"""
# 改造前 - 硬编码邮件模板
EMAIL_TEMPLATES = {
    "welcome": """
尊敬的{client_name}，您好！

欢迎选择{company_name}！

您的账户已成功开通，可以开始基金投资之旅。

【账户信息】
客户编号：{client_id}
开户日期：{open_date}
风险等级：{risk_level}

【下一步】
1. 完成风险测评
2. 绑定银行卡
3. 开始投资

如有任何问题，请随时联系我们：
客服热线：400-xxx-xxxx
官方网站：www.xxx.com

祝您投资顺利！

{company_name}
{send_date}
""",

    "monthly_statement": """
尊敬的{client_name}，您好！

您{month}月的对账单已生成，请查收附件。

【本月概要】
期初资产：{beginning_assets}
期末资产：{ending_assets}
本月收益：{monthly_return}

如有疑问，请联系您的客户经理或拨打客服热线。

{company_name}
{send_date}
""",

    "product_recommendation": """
尊敬的{client_name}，您好！

根据您的风险承受能力和投资偏好，我们为您推荐以下产品：

【推荐产品】
产品名称：{product_name}
产品类型：{product_type}
风险等级：{risk_level}
预期收益：{expected_return}

【推荐理由】
{recommendation_reason}

风险提示：基金有风险，投资需谨慎。本推荐仅供参考，不构成投资建议。

{company_name}
{send_date}
"""
}
"""

# ========== 文件 26: sms_templates.py (改造前) ==========
"""
# 改造前 - 硬编码短信模板
SMS_TEMPLATES = {
    "trade_confirm": "【{company}】您于{date}的{trade_type}申请已确认，确认份额{shares}份，确认净值{nav}元。",
    "dividend_notice": "【{company}】您持有的{fund_name}将于{date}分红，每10份派{dividend}元。",
    "redemption_arrival": "【{company}】您赎回的{fund_name}资金将于{date}到账，金额{amount}元。",
    "risk_warning": "【{company}】提示：您持有的{fund_name}近期波动较大，请注意投资风险。",
    "password_reset": "【{company}】您的验证码是{code}，5分钟内有效。如非本人操作，请忽略。",
    "account_security": "【{company}】您的账户于{time}在{device}登录，如非本人操作请及时联系客服。"
}
"""

# ========== 文件 27: audit_templates.py (改造前) ==========
"""
# 改造前 - 硬编码审计模板
INTERNAL_AUDIT_CHECKLIST = [
    {"area": "投资管理", "items": [
        "投资范围是否符合合同约定",
        "投资比例是否超限",
        "关联交易是否合规",
        "投资决策流程是否规范"
    ]},
    {"area": "估值核算", "items": [
        "估值方法是否一致",
        "估值结果是否准确",
        "异常价格是否处理",
        "估值调整是否审批"
    ]},
    {"area": "信息披露", "items": [
        "定期报告是否按时披露",
        "临时公告是否及时准确",
        "披露内容是否完整",
        "披露程序是否规范"
    ]},
    {"area": "销售合规", "items": [
        "适当性管理是否执行",
        "宣传材料是否合规",
        "客户投诉是否处理",
        "录音录像是否完整"
    ]}
]

AUDIT_FINDING_TEMPLATE = """
审计发现编号：{finding_id}
审计领域：{audit_area}
发现日期：{finding_date}

一、发现描述
{description}

二、涉及金额/范围
{scope}

三、潜在影响
{impact}

四、整改建议
{recommendations}

五、整改期限
{deadline}
"""
"""

# ========== 文件 28: regulatory_filing_templates.py (改造前) ==========
"""
# 改造前 - 硬编码监管报送模板
REGULATORY_REPORT_TEMPLATES = {
    "季度报告": """
基金管理公司季度报告
报告期：{quarter}

一、基本情况
公司 name：{company_name}
注册资本：{registered_capital}
管理规模：{aum}

二、经营情况
营业收入：{revenue}
净利润：{net_profit}
管理费用收入：{management_fee_income}

三、产品情况
产品数量：{product_count}
产品规模分布：{aum_distribution}

四、合规情况
合规事件：{compliance_incidents}
处罚情况：{penalties}
""",

    "年度审计": """
基金管理公司年度审计报告
审计年度：{year}

一、审计意见
{audit_opinion}

二、财务报表
资产负债表：{balance_sheet}
利润表：{income_statement}
现金流量表：{cash_flow}

三、重要事项
{significant_matters}

四、内部控制评价
{internal_control}
"""
}
"""

# ========== 文件 29: service_scripts.py (改造前) ==========
"""
# 改造前 - 硬编码服务话术
CUSTOMER_SERVICE_SCRIPTS = {
    "开场白": [
        "您好，欢迎致电{company_name}客服中心，我是客服专员{agent_name}，很高兴为您服务。",
        "您好，{company_name}客服热线，请问有什么可以帮您？"
    ],
    
    "hold": [
        "请您稍等，我为您查询一下。",
        "这个问题我需要确认一下，请稍候。",
        "正在为您处理，大约需要X分钟，请问您可以等待吗？"
    ],
    
    "transfer": [
        "这个问题需要转接专业部门处理，请稍候。",
        "我为您转接到投资顾问，请稍等。"
    ],
    
    "closing": [
        "感谢您的来电，祝您投资顺利，再见！",
        "还有其他可以帮您的吗？祝您生活愉快，再见！"
    ],
    
    "complaint_handling": [
        "非常抱歉给您带来不好的体验，我会认真记录您的问题。",
        "感谢您反馈这个问题，我们会尽快核实并给您答复。",
        "您的问题我已经记录，将在X个工作日内给您回复。"
    ]
}
"""

# ========== 文件 30: document_templates.py (改造前) ==========
"""
# 改造前 - 硬编码文档模板
DOCUMENT_TEMPLATES = {
    "风险测评问卷": """
投资者风险测评问卷

客户姓名：__________  客户编号：__________
测评日期：__________

一、财务状况
1. 您的家庭年收入约为？
   □ 10万以下  □ 10-30万  □ 30-50万  □ 50-100万  □ 100万以上

2. 可用于投资的资金占家庭总资产的比例？
   □ 10%以下  □ 10-30%  □ 30-50%  □ 50%以上

二、投资经验
3. 您的投资经验？
   □ 无经验  □ 1年以下  □ 1-3年  □ 3-5年  □ 5年以上

4. 您投资过的金融产品？（多选）
   □ 银行存款  □ 债券  □ 基金  □ 股票  □ 期货/期权  □ 其他

三、风险偏好
5. 您能接受的最大投资损失？
   □ 5%以内  □ 10%以内  □ 20%以内  □ 30%以内  □ 50%以上

评分结果：__________
风险等级：□保守型 □稳健型 □平衡型 □成长型 □进取型
""",

    "委托授权书": """
投资授权委托书

委托人：__________ 身份证号：__________
受托人：__________ 身份证号：__________

兹委托__________作为我的代理人，全权代理我办理以下事项：

一、代理事项
□ 基金账户开户  □ 基金认购  □ 基金申购  □ 基金赎回
□ 基金转换  □ 分红方式变更  □ 其他：__________

二、代理期限
自____年__月__日至____年__月__日

三、其他约定
__________________________________________

委托人签名：__________ 日期：__________
"""
}
"""

print("B类数据文件 (11-30) 定义完成 - 改造前版本")
print("这些数据需要改为JSON/YAML配置 + Jinja2模板")
