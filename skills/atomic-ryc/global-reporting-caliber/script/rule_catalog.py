"""Rule catalog for listed company reporting caliber validation.

This module defines a small, extensible rule set aimed at validating whether
company disclosures appear to match common regulatory reporting calibers.
The rules are intentionally heuristic and should be combined with legal review.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class RuleItem:
    rule_id: str
    topic: str
    severity: str
    description: str
    expected_keywords: List[str] = field(default_factory=list)
    negative_keywords: List[str] = field(default_factory=list)
    legal_basis: List[Dict[str, str]] = field(default_factory=list)
    checks: List[Dict[str, str]] = field(default_factory=list)


RULES: List[RuleItem] = [
    RuleItem(
        rule_id="DISC-001",
        topic="定期报告口径一致性",
        severity="high",
        description="年度/半年度/季度报告应明确报告期、合并范围与主要会计口径。",
        expected_keywords=["报告期", "合并报表", "财务报表", "会计政策", "会计估计"],
        legal_basis=[
            {
                "source": "中国证监会",
                "title": "上市公司信息披露管理办法",
                "focus": "真实、准确、完整、及时披露",
            },
            {
                "source": "中国证监会",
                "title": "公开发行证券的公司信息披露内容与格式准则（年报/半年报）",
                "focus": "报告期、财务数据、重大事项披露口径",
            },
        ],
        checks=[
            {"name": "presence", "pattern": "报告期"},
            {"name": "presence", "pattern": "合并"},
            {"name": "presence", "pattern": "会计政策"},
        ],
    ),
    RuleItem(
        rule_id="DISC-002",
        topic="关联交易报送口径",
        severity="high",
        description="关联交易披露应覆盖关联方、交易标的、定价依据、累计口径和审议程序。",
        expected_keywords=["关联交易", "关联方", "定价", "审议", "累计"],
        legal_basis=[
            {
                "source": "上交所/深交所",
                "title": "股票上市规则",
                "focus": "关联交易披露与审议标准",
            },
            {
                "source": "交易所",
                "title": "公告格式指引",
                "focus": "关联交易公告应披露的字段",
            },
        ],
        checks=[
            {"name": "presence", "pattern": "关联方"},
            {"name": "presence", "pattern": "定价"},
            {"name": "presence", "pattern": "董事会"},
        ],
    ),
    RuleItem(
        rule_id="DISC-003",
        topic="重大交易报送口径",
        severity="high",
        description="收购、出售资产、对外投资等重大交易应披露计算分母、占比和是否达审议/披露标准。",
        expected_keywords=["总资产", "营业收入", "净利润", "占比", "股东大会"],
        legal_basis=[
            {
                "source": "上交所/深交所",
                "title": "股票上市规则",
                "focus": "重大交易认定标准与累计计算口径",
            },
            {
                "source": "交易所",
                "title": "公告格式指引",
                "focus": "交易情况概述表和附件要求",
            },
        ],
        checks=[
            {"name": "presence", "pattern": "占比"},
            {"name": "presence", "pattern": "审议"},
            {"name": "presence", "pattern": "股东大会"},
        ],
    ),
    RuleItem(
        rule_id="DISC-004",
        topic="募集资金使用报送口径",
        severity="medium",
        description="募集资金使用披露应覆盖募集资金总额、用途变更、实施主体和进度。",
        expected_keywords=["募集资金", "用途", "变更", "实施主体", "进度"],
        legal_basis=[
            {
                "source": "中国证监会/交易所",
                "title": "募集资金管理相关规则",
                "focus": "募集资金使用与变更的信息披露",
            }
        ],
        checks=[
            {"name": "presence", "pattern": "募集资金"},
            {"name": "presence", "pattern": "实施主体"},
        ],
    ),
    RuleItem(
        rule_id="DISC-005",
        topic="会计政策/估计变更报送口径",
        severity="medium",
        description="会计政策或会计估计变更应披露依据、变更原因、追溯影响或当期影响。",
        expected_keywords=["会计政策变更", "会计估计变更", "追溯", "影响"],
        legal_basis=[
            {
                "source": "财政部/证监会/交易所",
                "title": "企业会计准则与交易所公告格式",
                "focus": "变更依据与影响披露",
            }
        ],
        checks=[
            {"name": "presence", "pattern": "影响"},
            {"name": "presence", "pattern": "依据"},
        ],
    ),
]


def to_dict() -> List[Dict[str, object]]:
    return [r.__dict__ for r in RULES]
