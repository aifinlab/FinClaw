"""Monthly companion report builder.

Usage:
python monthly_companion_report_builder.py --input sample.json --output report.md

Input JSON schema (minimal example):
{
"customer": {
    "name": "客户名称",
    "risk_level": "R3",
    "investment_goal": "稳健增值",
    "horizon_months": 24,
    "liquidity_constraints": "6个月内不动用"
},
"portfolio": {
    "as_of": "2026-02-28",
    "allocation": [
    {"asset_class": "固收", "weight": 0.55},
    {"asset_class": "权益", "weight": 0.25},
    {"asset_class": "另类", "weight": 0.20}
    ],
    "holdings": [
    {
        "product": "固收+1号",
        "type": "理财",
        "amount": 800000,
        "monthly_return": 0.004,
        "risk_note": "久期偏长"
    }
    ]
},
"market_view": {
    "summary": "市场震荡，固收稳定",
    "risk_warnings": ["权益波动抬升", "利率阶段性上行"]
},
"communications": {
    "key_concerns": ["回撤", "流动性"],
    "notes": "客户关注收益回撤原因"
},
"actions": [
    {"owner": "RM", "item": "解释回撤来源", "due": "2026-03-05"}
],
"pending": ["补充上月对比数据"]
}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data




@dataclass
class CustomerInfo:
    name: str = "未知客户"
    risk_level: str = "未提供"
    investment_goal: str = "未提供"
    horizon_months: Optional[int] = None
    liquidity_constraints: str = "未提供"


@dataclass
class PortfolioInfo:
    as_of: str = "未知日期"
    allocation: List[Dict[str, Any]] = field(default_factory=list)
    holdings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MarketView:
    summary: str = "未提供"
    risk_warnings: List[str] = field(default_factory=list)


@dataclass
class CommunicationInfo:
    key_concerns: List[str] = field(default_factory=list)
    notes: str = "未提供"


@dataclass
class ReportInput:
    customer: CustomerInfo
    portfolio: PortfolioInfo
    market_view: MarketView
    communications: CommunicationInfo
    actions: List[Dict[str, Any]] = field(default_factory=list)
    pending: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_input(data: Dict[str, Any]) -> ReportInput:
    customer = CustomerInfo(**data.get("customer", {}))
    portfolio = PortfolioInfo(**data.get("portfolio", {}))
    market_view = MarketView(**data.get("market_view", {}))
    communications = CommunicationInfo(**data.get("communications", {}))
    return ReportInput(
        customer=customer,
        portfolio=portfolio,
        market_view=market_view,
        communications=communications,
        actions=data.get("actions", []),
        pending=data.get("pending", []),
        assumptions=data.get("assumptions", []),
    )


def format_currency(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "未提供"
    return f"{amount:,.2f}"


def format_percentage(value: Any) -> str:
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        return "未提供"
    return f"{ratio * 100:.2f}%"


def render_allocation(allocation: List[Dict[str, Any]]) -> str:
    if not allocation:
        return "- 暂无配置数据"
    lines = []
    for item in allocation:
        asset_class = item.get("asset_class", "未命名")
        weight = format_percentage(item.get("weight"))
        lines.append(f"- {asset_class}：{weight}")
    return "\n".join(lines)


def render_holdings(holdings: List[Dict[str, Any]]) -> str:
    if not holdings:
        return "- 暂无持仓数据"
    lines = []
    for item in holdings:
        product = item.get("product", "未命名")
        product_type = item.get("type", "未提供")
        amount = format_currency(item.get("amount"))
        monthly_return = format_percentage(item.get("monthly_return"))
        risk_note = item.get("risk_note", "未提供")
        lines.append(
            f"- {product}（{product_type}），规模 {amount}，月度收益 {monthly_return}，风险提示：{risk_note}"
        )
    return "\n".join(lines)


def render_actions(actions: List[Dict[str, Any]]) -> str:
    if not actions:
        return "- 暂无新增行动项"
    lines = []
    for action in actions:
        owner = action.get("owner", "未指定")
        item = action.get("item", "未提供")
        due = action.get("due", "未提供")
        lines.append(f"- {item}（负责人：{owner}，计划完成：{due}）")
    return "\n".join(lines)


def render_pending(pending: List[str]) -> str:
    if not pending:
        return "- 暂无待确认事项"
    return "\n".join(f"- {item}" for item in pending)


def render_assumptions(assumptions: List[str]) -> str:
    if not assumptions:
        return "- 无"
    return "\n".join(f"- {item}" for item in assumptions)


def build_report(data: ReportInput) -> str:
    report_date = datetime.now().strftime("%Y-%m-%d")
    horizon = (
        f"{data.customer.horizon_months}个月" if data.customer.horizon_months else "未提供"
    )
    concerns = (
        "、".join(data.communications.key_concerns)
        if data.communications.key_concerns
        else "未提供"
    )
    risk_warnings = (
        "、".join(data.market_view.risk_warnings)
        if data.market_view.risk_warnings
        else "未提供"
    )

    return f"""# 客户陪伴月报

- 报告日期：{report_date}
- 客户：{data.customer.name}
- 风险等级：{data.customer.risk_level}
- 投资目标：{data.customer.investment_goal}
- 投资期限：{horizon}
- 流动性约束：{data.customer.liquidity_constraints}

## 一、月度复盘摘要
- 本月核心市场观点：{data.market_view.summary}
- 客户关注点：{concerns}
- 主要风险提示：{risk_warnings}

## 二、组合与持仓回顾
- 统计口径日期：{data.portfolio.as_of}
- 资产配置概览：
{render_allocation(data.portfolio.allocation)}
- 核心持仓回顾：
{render_holdings(data.portfolio.holdings)}

## 三、风险与波动解释
- 主要风险来源：{risk_warnings}
- 持仓提示：如存在单一品类集中或久期偏长，请在沟通中重点说明。

## 四、客户沟通要点与回应
- 沟通记录摘要：{data.communications.notes}
- 重点回应建议：围绕客户关切点进行收益来源解释与风险提示。

## 五、下月关注事项与行动清单
{render_actions(data.actions)}

## 六、待确认事项
{render_pending(data.pending)}

## 七、假设与限制
{render_assumptions(data.assumptions)}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Monthly companion report builder")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", required=True, help="Path to output markdown")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = parse_input(load_json(input_path))
    report = build_report(data)

    output_path.write_text(report, encoding="utf-8")
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    main()
