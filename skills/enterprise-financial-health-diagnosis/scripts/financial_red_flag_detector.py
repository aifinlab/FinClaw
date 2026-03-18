#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于财务指标和简单规则识别财务红旗。
"""

from __future__ import annotations
import json
import sys
from typing import Dict, Any, List


def detect_flags(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    flags = []

    revenue_growth = data.get("营业收入增长率")
    profit_growth = data.get("净利润增长率")
    receivable_growth = data.get("应收账款增长率")
    inventory_growth = data.get("存货增长率")
    debt_ratio = data.get("资产负债率")
    op_cf = data.get("经营活动现金流净额")
    net_profit = data.get("净利润")
    ocf_np = data.get("利润现金匹配比")
    short_debt_growth = data.get("短期借款增长率")
    non_recurring_ratio = data.get("非经常性损益占净利润比")
    audit_opinion = data.get("审计意见")

    if revenue_growth is not None and receivable_growth is not None and receivable_growth > revenue_growth + 0.2:
        flags.append({
            "item": "应收账款扩张快于收入增长",
            "basis": f"应收账款增长率为 {receivable_growth:.2%}，高于营业收入增长率 {revenue_growth:.2%}",
            "impact": "可能存在回款变慢、信用销售扩张或收入质量承压",
            "follow_up": "补充账龄结构、前五大客户回款、逾期明细"
        })

    if inventory_growth is not None and revenue_growth is not None and inventory_growth > revenue_growth + 0.2:
        flags.append({
            "item": "存货增长明显快于收入增长",
            "basis": f"存货增长率为 {inventory_growth:.2%}，高于营业收入增长率 {revenue_growth:.2%}",
            "impact": "可能存在库存积压、产品滞销或备货失衡",
            "follow_up": "补充存货分类、库龄结构、跌价准备计提依据"
        })

    if ocf_np is not None and ocf_np < 0.5 and (net_profit or 0) > 0:
        flags.append({
            "item": "利润与现金匹配度偏弱",
            "basis": f"利润现金匹配比为 {ocf_np:.2f}",
            "impact": "利润含金量偏低，需关注收入确认、回款质量和营运资本占用",
            "follow_up": "补充现金流拆解、应收与预付款明细"
        })

    if op_cf is not None and op_cf < 0 and (net_profit or 0) > 0:
        flags.append({
            "item": "净利润为正但经营现金流为负",
            "basis": "企业账面盈利与现金回流表现不一致",
            "impact": "可能影响真实偿债能力和流动性安全边际",
            "follow_up": "核验收入确认、回款节奏、预付与存货变化"
        })

    if debt_ratio is not None and debt_ratio > 0.75:
        flags.append({
            "item": "杠杆水平偏高",
            "basis": f"资产负债率为 {debt_ratio:.2%}",
            "impact": "债务负担较重，权益缓冲相对不足",
            "follow_up": "补充债务期限结构、授信集中度、还本付息安排"
        })

    if short_debt_growth is not None and short_debt_growth > 0.3:
        flags.append({
            "item": "短期借款增长较快",
            "basis": f"短期借款增长率为 {short_debt_growth:.2%}",
            "impact": "可能反映短期资金压力上升或融资依赖增强",
            "follow_up": "补充新增借款用途、到期分布及续贷安排"
        })

    if non_recurring_ratio is not None and non_recurring_ratio > 0.4:
        flags.append({
            "item": "利润对非经常性项目依赖较高",
            "basis": f"非经常性损益占净利润比为 {non_recurring_ratio:.2%}",
            "impact": "盈利可持续性存在不确定性",
            "follow_up": "补充非经常性损益构成及未来可持续性说明"
        })

    if audit_opinion in {"保留意见", "无法表示意见", "否定意见"}:
        flags.append({
            "item": "审计意见存在重大关注",
            "basis": f"审计意见为 {audit_opinion}",
            "impact": "财务信息可靠性或持续经营能力可能存在重要问题",
            "follow_up": "补充审计报告全文及相关事项整改说明"
        })

    return flags


def main():
    if len(sys.argv) < 2:
        print("用法：python financial_red_flag_detector.py 输入.json [输出.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = detect_flags(data)
    text = json.dumps(result, ensure_ascii=False, indent=2)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
