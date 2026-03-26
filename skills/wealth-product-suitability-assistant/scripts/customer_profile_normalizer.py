from __future__ import annotations
from typing import Any, Dict, List
import json

def normalize_customer_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    customer = payload.get("customer", {})
    profile = {
        "客户名称": customer.get("name", "未提供"),
        "风险等级": customer.get("risk_level", "未提供"),
        "投资目标": customer.get("investment_goal", "未提供"),
        "可投资期限(月)": customer.get("investment_horizon_months"),
        "流动性需求": customer.get("liquidity_need", "未提供"),
        "年龄": customer.get("age"),
        "职业": customer.get("occupation", "未提供"),
        "收入稳定性": customer.get("income_stability", "未提供"),
        "现有配置": customer.get("current_allocation", []),
        "待核验事项": [],
    }

    if not profile["风险等级"] or profile["风险等级"] == "未提供":
        profile["待核验事项"].append("缺少客户风险等级")
    if profile["可投资期限(月)"] is None:
        profile["待核验事项"].append("缺少可投资期限信息")
    if not profile["流动性需求"] or profile["流动性需求"] == "未提供":
        profile["待核验事项"].append("缺少流动性需求信息")
    if not profile["投资目标"] or profile["投资目标"] == "未提供":
        profile["待核验事项"].append("缺少投资目标信息")

    return profile

if __name__ == "__main__":
    demo = {
        "customer": {
            "name": "张三",
            "risk_level": "稳健型",
            "investment_goal": "稳健增值",
            "investment_horizon_months": 12,
            "liquidity_need": "中",
            "age": 42,
            "occupation": "企业管理人员",
            "income_stability": "较稳定",
            "current_allocation": ["存款偏高", "权益类偏低"]
        }
    }
    print(json.dumps(normalize_customer_profile(demo), ensure_ascii=False, indent=2))
