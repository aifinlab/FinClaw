#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List
import json

PRODUCT_RULES = {
    "账户管理方案": ["账户", "权限", "集团", "可视化", "母子公司"],
    "收款管理方案": ["收款", "回款", "对账", "渠道", "识别"],
    "付款管理方案": ["付款", "代发", "审批", "批量", "内控"],
    "资金归集方案": ["归集", "头寸", "流动性", "调拨", "集中"],
    "票据结算方案": ["票据", "贴现", "票据池"],
    "供应链结算方案": ["供应链", "上下游", "链上", "应收", "应付"],
    "跨境结算方案": ["跨境", "外币", "国际结算", "信用证", "保函"],
    "银企直联方案": ["ERP", "司库", "接口", "API", "银企直联"],
}

def match_products(customer_profile: Dict) -> List[Dict]:
    text_parts = []
    for value in customer_profile.values():
        if isinstance(value, str):
            text_parts.append(value)
        elif isinstance(value, list):
            text_parts.extend([str(x) for x in value])
    text = " ".join(text_parts)

    results = []
    for product, keywords in PRODUCT_RULES.items():
        hit = sum(1 for kw in keywords if kw in text)
        if hit > 0:
            results.append({
                "方案": product,
                "命中关键词数": hit,
                "匹配理由": [kw for kw in keywords if kw in text]
            })

    results.sort(key=lambda x: x["命中关键词数"], reverse=True)
    return results

if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    print(json.dumps(match_products(data), ensure_ascii=False, indent=2))
