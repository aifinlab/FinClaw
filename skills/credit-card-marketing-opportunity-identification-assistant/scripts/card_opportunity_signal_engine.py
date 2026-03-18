from __future__ import annotations
import json
from typing import Any, Dict, List

def score_customer_opportunity(customer: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    reasons: List[str] = []
    opportunity_types: List[str] = []

    if not customer.get("has_credit_card", False):
        if customer.get("debit_activity_level", 0) >= 7:
            score += 20
            reasons.append("借记卡活跃度较高，存在首卡获客基础。")
            opportunity_types.append("首卡获客")
        if customer.get("salary_payment", False):
            score += 15
            reasons.append("存在工资代发关系，客户关系深度较好。")
        if customer.get("ecommerce_spend_ratio", 0) >= 0.3:
            score += 10
            reasons.append("线上消费占比较高，适合线上权益型信用卡。")
        if customer.get("travel_frequency", 0) >= 4:
            score += 10
            reasons.append("出行场景较活跃，存在商旅卡或出行权益卡机会。")

    else:
        if not customer.get("card_activated", True):
            score += 18
            reasons.append("已持卡未激活，存在激活促活机会。")
            opportunity_types.append("激活促活")
        if customer.get("monthly_card_txn_count", 0) <= 2:
            score += 10
            reasons.append("持卡活跃度较低，存在促活空间。")
            opportunity_types.append("低活跃促活")
        if customer.get("credit_utilization", 0) >= 0.75:
            score += 12
            reasons.append("额度使用率较高，存在升额经营机会。")
            opportunity_types.append("升额经营")
        if customer.get("installment_acceptance", 0) >= 0.6:
            score += 8
            reasons.append("历史上对分期接受度较高，存在分期推荐机会。")
            opportunity_types.append("分期经营")
        if customer.get("family_finance_relation", False):
            score += 6
            reasons.append("存在明显家庭金融关系，可关注附属卡机会。")
            opportunity_types.append("附属卡拓展")

    if customer.get("app_login_days_30d", 0) >= 10:
        score += 8
        reasons.append("近 30 天 App 活跃度较高，适合站内触达。")
    if customer.get("campaign_click_rate", 0) >= 0.2:
        score += 6
        reasons.append("营销活动点击率较高，说明活动响应度较好。")

    level = "低"
    if score >= 45:
        level = "高"
    elif score >= 25:
        level = "中"

    return {
        "customer_id": customer.get("customer_id"),
        "score": score,
        "opportunity_level": level,
        "opportunity_types": sorted(set(opportunity_types)),
        "reasons": reasons,
        "primary_channel": "App站内推荐" if customer.get("app_login_days_30d", 0) >= 10 else "客户经理外呼",
    }

def run(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [score_customer_opportunity(c) for c in customers]

if __name__ == "__main__":
    demo = [
        {
            "customer_id": "C001",
            "has_credit_card": False,
            "debit_activity_level": 8,
            "salary_payment": True,
            "ecommerce_spend_ratio": 0.42,
            "travel_frequency": 5,
            "app_login_days_30d": 15,
            "campaign_click_rate": 0.25,
        }
    ]
    print(json.dumps(run(demo), ensure_ascii=False, indent=2))
