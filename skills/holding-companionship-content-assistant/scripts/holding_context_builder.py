from __future__ import annotations

from typing import Any, Dict, List
import json


def normalize_holding_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    """标准化客户持仓与陪伴场景输入。"""
    customer = payload.get("customer", {}) or {}
    holdings = payload.get("holdings", []) or []
    market_context = payload.get("market_context", {}) or {}

    total_amount = 0.0
    normalized_holdings: List[Dict[str, Any]] = []
    for item in holdings:
        amount = float(item.get("amount", 0) or 0)
        total_amount += amount
        normalized_holdings.append(
            {
                "product_name": item.get("product_name", "未知产品"),
                "product_type": item.get("product_type", "未分类"),
                "amount": amount,
                "profit_loss": float(item.get("profit_loss", 0) or 0),
                "risk_level": item.get("risk_level", "未知"),
            }
        )

    for item in normalized_holdings:
        item["weight"] = round(item["amount"] / total_amount, 4) if total_amount else 0.0

    return {
        "customer_segment": customer.get("segment", "未提供"),
        "risk_profile": customer.get("risk_profile", "未提供"),
        "investment_horizon": customer.get("investment_horizon", "未提供"),
        "liquidity_preference": customer.get("liquidity_preference", "未提供"),
        "communication_goal": payload.get("communication_goal", "持仓陪伴"),
        "channel": payload.get("channel", "微信"),
        "market_theme": market_context.get("theme", "未提供"),
        "market_summary": market_context.get("summary", "未提供"),
        "holding_count": len(normalized_holdings),
        "total_amount": round(total_amount, 2),
        "holdings": normalized_holdings,
        "missing_information": _find_missing(customer, holdings, market_context),
    }


def _find_missing(customer: Dict[str, Any], holdings: List[Dict[str, Any]], market_context: Dict[str, Any]) -> List[str]:
    missing = []
    if not customer.get("risk_profile"):
        missing.append("客户风险承受能力")
    if not holdings:
        missing.append("客户持仓清单")
    if holdings and all(not h.get("product_type") for h in holdings):
        missing.append("产品类别")
    if not market_context.get("summary"):
        missing.append("近期市场背景说明")
    return missing


if __name__ == "__main__":
    sample = {
        "customer": {"segment": "重点财富客户", "risk_profile": "中风险", "investment_horizon": "3年以上"},
        "holdings": [
            {"product_name": "稳健债券理财", "product_type": "固收+", "amount": 500000, "profit_loss": -12000, "risk_level": "中低"},
            {"product_name": "权益精选基金", "product_type": "权益基金", "amount": 300000, "profit_loss": -45000, "risk_level": "中高"},
        ],
        "market_context": {"theme": "权益波动加大", "summary": "近期权益市场震荡加剧，成长风格回撤明显。"},
        "communication_goal": "解释波动并稳定客户预期",
        "channel": "电话",
    }
    print(json.dumps(normalize_holding_context(sample), ensure_ascii=False, indent=2))
