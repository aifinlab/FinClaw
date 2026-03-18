"""贷前风险信号解析器。

输入：一个字典，包含申请信息、财务摘要、信用摘要、司法摘要等。
输出：按维度归类的风险信号列表。
"""

from __future__ import annotations

from typing import Dict, List, Any


def parse_risk_signals(data: Dict[str, Any]) -> Dict[str, List[str]]:
    result = {
        "entity": [],
        "operation": [],
        "finance": [],
        "credit": [],
        "judicial_compliance": [],
        "transaction_and_use": [],
        "consistency": [],
        "fraud_behavior": [],
    }

    entity = data.get("entity", {})
    operation = data.get("operation", {})
    finance = data.get("finance", {})
    credit = data.get("credit", {})
    judicial = data.get("judicial", {})
    transaction = data.get("transaction", {})
    consistency = data.get("consistency", {})
    fraud = data.get("fraud", {})

    if entity.get("entity_age_years", 99) < 1:
        result["entity"].append("主体成立时间较短，需要关注经营稳定性与业务真实性。")
    if entity.get("frequent_registration_change"):
        result["entity"].append("工商信息近期频繁变更，需要核验变更原因及经营连续性。")

    if operation.get("customer_concentration", 0) >= 0.5:
        result["operation"].append("客户集中度偏高，需关注对单一客户依赖风险。")
    if operation.get("revenue_volatility_high"):
        result["operation"].append("经营收入波动较大，需进一步核验收入稳定性。")

    if finance.get("cash_flow_negative_continuous"):
        result["finance"].append("经营现金流持续偏弱，需关注还款来源质量。")
    if finance.get("asset_liability_ratio", 0) > 0.75:
        result["finance"].append("资产负债率偏高，需关注杠杆与偿债压力。")
    if finance.get("profit_cash_mismatch"):
        result["finance"].append("利润与现金流不匹配，需关注盈利质量。")

    if credit.get("current_overdue"):
        result["credit"].append("存在当前逾期记录，属于高优先级信用风险。")
    if credit.get("recent_query_count", 0) >= 6:
        result["credit"].append("近期征信查询次数偏多，存在多头申请或资金紧张可能。")
    if credit.get("multi_borrowing"):
        result["credit"].append("存在多头借贷迹象，需核验总负债与偿债能力。")

    if judicial.get("executed_case_count", 0) > 0:
        result["judicial_compliance"].append("存在被执行记录，需重点关注司法与履约风险。")
    if judicial.get("major_penalty"):
        result["judicial_compliance"].append("存在重大处罚或合规争议，需要进一步审查。")

    if transaction.get("loan_use_unclear"):
        result["transaction_and_use"].append("贷款用途描述不清，需补充用途证明与资金流向说明。")
    if transaction.get("fund_return_signals"):
        result["transaction_and_use"].append("存在疑似资金回流或交易闭环不足迹象。")

    if consistency.get("material_conflict"):
        result["consistency"].append("申请材料之间存在前后冲突，需要人工复核。")
    if consistency.get("income_mismatch"):
        result["consistency"].append("申报收入与流水/经营表现不一致，需要核验真实性。")

    if fraud.get("suspected_forgery"):
        result["fraud_behavior"].append("存在资料伪造或篡改嫌疑，应升级复核。")
    if fraud.get("abnormal_application_pattern"):
        result["fraud_behavior"].append("申请行为模式异常，需要排查欺诈风险。")

    return result


if __name__ == "__main__":
    demo = {
        "entity": {"entity_age_years": 0.5, "frequent_registration_change": True},
        "operation": {"customer_concentration": 0.62, "revenue_volatility_high": True},
        "finance": {"cash_flow_negative_continuous": True, "asset_liability_ratio": 0.82},
        "credit": {"current_overdue": False, "recent_query_count": 8, "multi_borrowing": True},
        "judicial": {"executed_case_count": 1},
        "transaction": {"loan_use_unclear": True},
        "consistency": {"material_conflict": True},
        "fraud": {"abnormal_application_pattern": True},
    }
    parsed = parse_risk_signals(demo)
    for k, v in parsed.items():
        print(f"[{k}]")
        for item in v:
            print("-", item)
