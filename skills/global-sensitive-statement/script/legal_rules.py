from __future__ import annotations

LEGAL_BASES = [
    {
        "id": "LAW-SEC-INFO-01",
        "name": "《中华人民共和国证券法》信息披露要求",
        "source": "中国证监会法规正文",
        "url": "https://neris.csrc.gov.cn/falvfagui/rdqsHeader/mainbody?navbarId=1&secFutrsLawId=0fc431a2a10b47909beef058f6ac3335",
        "summary": "信息披露义务人应当及时依法履行信息披露义务，披露的信息应当真实、准确、完整，简明清晰、通俗易懂。",
    },
    {
        "id": "RULE-CSRC-182-03",
        "name": "《上市公司信息披露管理办法》第三条",
        "source": "中国证监会",
        "url": "https://www.csrc.gov.cn/csrc/c106256/c1653948/content.shtml",
        "summary": "上市公司披露的信息不得有虚假记载、误导性陈述或者重大遗漏。",
    },
    {
        "id": "RULE-SZSE-G2-2025",
        "name": "《深圳证券交易所上市公司自律监管指南第2号——公告格式（2025年修订）》",
        "source": "深圳证券交易所",
        "url": "https://docs.static.szse.cn/www/lawrules/service/share/W020250425747814520529.pdf",
        "summary": "上市公司和相关信息披露义务人应当按照公告格式编制公告，并声明内容不存在虚假记载、误导性陈述或者重大遗漏。",
    },
]

SENSITIVE_PATTERNS = [
    {
        "category": "绝对化/保证性表述",
        "risk_level": "high",
        "patterns": [
            r"绝对",
            r"保证(?!.*真实、准确、完整)",
            r"毫无风险",
            r"稳赚不赔",
            r"必然",
            r"一定会",
            r"肯定会",
            r"完全不会",
            r"不存在任何风险",
            r"无条件实现",
        ],
        "why": "绝对化或保证收益式表述容易构成误导性陈述，需重点复核事实基础与限定条件。",
        "legal_basis": ["LAW-SEC-INFO-01", "RULE-CSRC-182-03"],
    },
    {
        "category": "预测性表述",
        "risk_level": "medium",
        "patterns": [
            r"预计",
            r"有望",
            r"或将",
            r"将(进一步|持续|显著|明显|实现|提升|增长)",
            r"预期",
            r"可能",
            r"存在.*可能",
            r"目标是",
            r"计划",
        ],
        "why": "预测、计划或展望类表述通常需要同时提示依据、假设前提和不确定性。",
        "legal_basis": ["LAW-SEC-INFO-01", "RULE-CSRC-182-03"],
    },
    {
        "category": "重大事项触发词",
        "risk_level": "medium",
        "patterns": [
            r"重大影响",
            r"重大不确定性",
            r"重大风险",
            r"实质性影响",
            r"重大变化",
            r"重大事项",
            r"特别提示",
            r"风险提示",
        ],
        "why": "出现重大事项或重大风险表述时，应检查是否有完整、充分、可读的风险揭示。",
        "legal_basis": ["RULE-CSRC-182-03", "RULE-SZSE-G2-2025"],
    },
    {
        "category": "未完成/待确认表述",
        "risk_level": "medium",
        "patterns": [
            r"尚未",
            r"未经审计",
            r"初步测算",
            r"以.*为准",
            r"待审议",
            r"待批准",
            r"待确认",
            r"存在分歧",
            r"可能调整",
        ],
        "why": "未完成、未经审计或待确认信息容易引发理解偏差，应审查是否充分提示口径边界。",
        "legal_basis": ["LAW-SEC-INFO-01", "RULE-SZSE-G2-2025"],
    },
    {
        "category": "风险揭示词",
        "risk_level": "info",
        "patterns": [
            r"风险",
            r"不确定性",
            r"敬请.*注意投资风险",
            r"谨慎决策",
            r"特别风险提示",
        ],
        "why": "风险揭示词本身不代表违规，但可作为判断预测性表述是否伴随充分风险说明的辅助信号。",
        "legal_basis": ["RULE-CSRC-182-03", "RULE-SZSE-G2-2025"],
    },
]

DEFAULT_COMPANY = {
    "name": "立讯精密工业股份有限公司",
    "ticker": "002475.SZ",
    "exchange": "深圳证券交易所",
    "public_sources": [
        {
            "type": "company_report_pdf",
            "label": "2025年半年度报告全文",
            "url": "https://static.cninfo.com.cn/finalpage/2025-08-26/1224571100.PDF",
        },
        {
            "type": "company_notice_pdf",
            "label": "2025年半年度业绩预告",
            "url": "https://static.cninfo.com.cn/finalpage/2025-04-26/1223326842.PDF",
        },
    ],
}
