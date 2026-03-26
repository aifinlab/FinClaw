#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
投诉分类脚本
输入：投诉记录列表
输出：为每条记录补充主分类、次分类和关键词命中信息
"""

from __future__ import annotations
import json
from typing import Any, Dict, List
import argparse

CATEGORY_RULES = {
    "服务态度类": ["态度差", "冷漠", "敷衍", "推诿", "不耐烦", "服务差"],
    "处理时效类": ["太慢", "迟迟", "一直没处理", "超时", "催了很多次", "未回复"],
    "收费争议类": ["手续费", "扣费", "利息", "违约金", "收费", "费用"],
    "规则解释类": ["没说清楚", "规则", "权益", "条款", "提示不足", "口径不一致"],
    "产品功能类": ["功能不能用", "权益没到账", "无法办理", "功能异常"],
    "系统异常类": ["报错", "闪退", "卡顿", "失败", "状态不对", "收不到短信"],
    "误导营销类": ["误导", "宣传不符", "承诺了", "说好的", "营销"],
    "流程体验类": ["流程复杂", "反复提交", "材料太多", "来回跑", "重复操作"],
}


def classify_text(text: str) -> Dict[str, Any]:
    text = text or ""
    hits = []
    for category, keywords in CATEGORY_RULES.items():
        matched = [kw for kw in keywords if kw in text]
        if matched:
            hits.append(
                {"category": category, "keywords": matched, "score": len(matched)})
    hits.sort(key=lambda x: x["score"], reverse=True)
    main_category = hits[0]["category"] if hits else "其他特殊类"
    sub_categories = [item["category"] for item in hits[1:3]]
    return {
        "main_category": main_category,
        "sub_categories": sub_categories,
        "matched_rules": hits,
    }


def classify_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    output = []
    for item in records:
        text = " ".join(str(item.get(k, ""))
                        for k in ["title", "content", "summary", "customer_request"])
        result = classify_text(text)
        merged = dict(item)
        merged.update(result)
        output.append(merged)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="投诉分类脚本")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        records = json.load(f)

    result = classify_records(records)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
