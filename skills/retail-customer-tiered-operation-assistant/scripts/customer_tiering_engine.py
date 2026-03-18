#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, List


def to_number(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def score_customer(customer: Dict) -> Dict:
    aum = to_number(customer.get("AUM", 0))
    deposit = to_number(customer.get("存款", 0))
    product_count = int(to_number(customer.get("产品持有数", 0)))
    txn_count = int(to_number(customer.get("近90天交易笔数", 0)))
    login_days = int(to_number(customer.get("近30天登录天数", 0)))
    salary_flag = 1 if str(customer.get("是否代发客户", "否")) == "是" else 0
    mortgage_flag = 1 if str(customer.get("是否房贷客户", "否")) == "是" else 0
    complaint_flag = 1 if str(customer.get("是否近期投诉", "否")) == "是" else 0
    asset_drop = to_number(customer.get("近90天资产下降比例", 0))

    value_score = min(40, aum / 50000 * 5 + deposit / 50000 * 2 + product_count * 2)
    activity_score = min(25, txn_count * 0.6 + login_days * 0.8)
    potential_score = min(20, salary_flag * 8 + mortgage_flag * 8 + product_count)
    risk_score = 0
    if complaint_flag:
        risk_score += 8
    if asset_drop >= 0.3:
        risk_score += 10
    elif asset_drop >= 0.15:
        risk_score += 5

    total = round(value_score + activity_score + potential_score - risk_score, 2)

    if complaint_flag or asset_drop >= 0.3:
        tier = "流失挽留层"
    elif total >= 60:
        tier = "重点维护层"
    elif total >= 42:
        tier = "潜力提升层"
    elif total >= 25:
        tier = "经营转化层"
    else:
        tier = "唤醒激活层"

    return {
        "客户标识": customer.get("客户标识", "未知客户"),
        "总分": total,
        "层级": tier,
        "价值分": round(value_score, 2),
        "活跃分": round(activity_score, 2),
        "潜力分": round(potential_score, 2),
        "风险扣分": round(risk_score, 2),
    }


def batch_tier(customers: List[Dict]) -> List[Dict]:
    results = [score_customer(c) for c in customers]
    results.sort(key=lambda x: x["总分"], reverse=True)
    return results


if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    if isinstance(data, dict):
        print(json.dumps(score_customer(data), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(batch_tier(data), ensure_ascii=False, indent=2))
