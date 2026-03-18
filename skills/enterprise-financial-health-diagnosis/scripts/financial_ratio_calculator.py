#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
根据财务原始数据计算核心指标。
输入 JSON 可以是单期，也可以是多期列表。
"""

from __future__ import annotations
import json
import sys
from typing import Dict, Any, List


def safe_div(a, b):
    if b in (0, None):
        return None
    try:
        return a / b
    except Exception:
        return None


def avg(a, b):
    if a is None or b is None:
        return None
    return (a + b) / 2


def calc_metrics(row: Dict[str, Any]) -> Dict[str, Any]:
    assets = row.get("总资产")
    liabilities = row.get("总负债")
    current_assets = row.get("流动资产")
    current_liabilities = row.get("流动负债")
    inventory = row.get("存货", 0) or 0
    prepayments = row.get("预付款项", 0) or 0
    revenue = row.get("营业收入")
    cost = row.get("营业成本")
    net_profit = row.get("净利润")
    ebit = row.get("息税前利润")
    interest = row.get("利息支出")
    op_cf = row.get("经营活动现金流净额")
    capex = row.get("资本性支出")
    receivables_avg = row.get("平均应收账款")
    inventory_avg = row.get("平均存货")
    assets_avg = row.get("平均总资产")

    return {
        "资产负债率": safe_div(liabilities, assets),
        "流动比率": safe_div(current_assets, current_liabilities),
        "速动比率": safe_div((current_assets or 0) - inventory - prepayments, current_liabilities),
        "利息保障倍数": safe_div(ebit, interest),
        "毛利率": safe_div((revenue or 0) - (cost or 0), revenue),
        "净利率": safe_div(net_profit, revenue),
        "总资产报酬水平": safe_div(net_profit, assets_avg),
        "应收账款周转率": safe_div(revenue, receivables_avg),
        "存货周转率": safe_div(cost, inventory_avg),
        "总资产周转率": safe_div(revenue, assets_avg),
        "利润现金匹配比": safe_div(op_cf, net_profit),
        "自由现金流": None if op_cf is None else op_cf - (capex or 0),
    }


def main():
    if len(sys.argv) < 2:
        print("用法：python financial_ratio_calculator.py 输入.json [输出.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        result = calc_metrics(data)
    elif isinstance(data, list):
        result = []
        for row in data:
            item = dict(row)
            item["指标"] = calc_metrics(row)
            result.append(item)
    else:
        raise ValueError("输入必须为对象或对象列表")

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
