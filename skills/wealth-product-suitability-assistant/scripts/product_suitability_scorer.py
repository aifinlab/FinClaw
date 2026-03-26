from __future__ import annotations
from typing import Any, Dict, List
import json

RISK_ORDER = {
    "保守型": 1,
    "稳健型": 2,
    "平衡型": 3,
    "进取型": 4,
}

PRODUCT_RISK_ORDER = {
    "低": 1,
    "中低": 2,
    "中": 3,
    "中高": 4,
    "高": 5,
}

def score_product(customer: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    warnings: List[str] = []
    penalties = 0
    score = 100

    customer_risk = RISK_ORDER.get(customer.get("risk_level"), 0)
    product_risk = PRODUCT_RISK_ORDER.get(product.get("risk_level"), 0)

    if customer_risk == 0:
        penalties += 25
        warnings.append("缺少客户风险等级，无法完成高置信度适配判断")
    elif product_risk > customer_risk + 1:
        penalties += 60
        warnings.append("产品风险等级明显高于客户承受能力，不建议推荐")
    elif product_risk > customer_risk:
        penalties += 25
        warnings.append("产品风险等级略高于客户风险承受能力，需审慎评估")
    else:
        reasons.append("产品风险等级与客户风险承受能力总体匹配")

    horizon = customer.get("investment_horizon_months")
    product_term = product.get("term_months")
    if horizon is None or product_term is None:
        penalties += 15
        warnings.append("期限信息不完整，期限匹配度仅供参考")
    elif product_term <= horizon:
        reasons.append("产品期限与客户可投资期限总体匹配")
    else:
        penalties += 20
        warnings.append("产品期限长于客户可投资期限，存在期限错配")

    liquidity_need = customer.get("liquidity_need", "未提供")
    liquidity = product.get("liquidity", "未提供")
    if liquidity_need == "高" and liquidity in {"低", "封闭"}:
        penalties += 25
        warnings.append("客户流动性需求较高，但产品流动性较弱")
    elif liquidity_need != "未提供":
        reasons.append("产品流动性与客户资金安排基本匹配")

    goal = customer.get("investment_goal", "")
    product_tag = product.get("goal_tag", "")
    if goal and product_tag and goal == product_tag:
        reasons.append("产品定位与客户投资目标较为一致")
    elif goal and product_tag:
        penalties += 10
        warnings.append("产品定位与客户投资目标存在一定偏差")

    complexity = product.get("complexity", "普通")
    if complexity == "复杂":
        penalties += 10
        warnings.append("产品结构较复杂，需加强风险揭示与适当性确认")

    score = max(0, score - penalties)
    if score >= 80:
        grade = "高适配"
    elif score >= 60:
        grade = "中适配"
    elif score >= 40:
        grade = "低适配"
    else:
        grade = "暂不建议"

    return {
        "产品名称": product.get("name", "未命名产品"),
        "适配得分": score,
        "适配等级": grade,
        "推荐理由": reasons,
        "风险提示": warnings,
    }

if __name__ == "__main__":
    customer = {
        "risk_level": "稳健型",
        "investment_horizon_months": 12,
        "liquidity_need": "中",
        "investment_goal": "稳健增值",
    }
    products = [
        {"name": "稳盈12M", "risk_level": "中低", "term_months": 12, "liquidity": "中", "goal_tag": "稳健增值", "complexity": "普通"},
        {"name": "高弹性增强", "risk_level": "中高", "term_months": 18, "liquidity": "低", "goal_tag": "收益增强", "complexity": "复杂"},
    ]
    print(json.dumps([score_product(customer, p) for p in products], ensure_ascii=False, indent=2))
