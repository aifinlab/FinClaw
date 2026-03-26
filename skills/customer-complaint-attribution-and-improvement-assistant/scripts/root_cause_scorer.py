#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
投诉根因打分脚本
基于规则为可能根因打分，输出主因、次因和解释。
"""

from __future__ import annotations
import json
from typing import Any, Dict, List
import argparse

CAUSE_RULES = {
    "产品规则问题": ["条款", "权益", "限制条件", "收费规则", "规则不清"],
    "流程设计问题": ["流程复杂", "反复提交", "材料", "审批慢", "流转"],
    "系统能力问题": ["报错", "闪退", "失败", "不同步", "系统"],
    "服务执行问题": ["态度", "解释不清", "推诿", "承诺不一致", "客服"],
    "管理与机制问题": ["培训不足", "质检", "升级机制", "监控", "长期没人处理"],
    "外部因素": ["合作机构", "商户", "通道", "清算", "政策变化"],
}


def score_causes(text: str) -> List[Dict[str, Any]]:
    text = text or ""
    scores = []
    for cause, keywords in CAUSE_RULES.items():
        matched = [kw for kw in keywords if kw in text]
        if matched:
            scores.append({
                "cause": cause,
                "score": len(matched),
                "evidence_keywords": matched,
            })
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores


def analyze_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for item in records:
        text = " ".join(str(item.get(k, ""))
                        for k in ["title", "content", "summary", "processing_note"])
        scores = score_causes(text)
        merged = dict(item)
        merged["cause_scores"] = scores
        merged["primary_cause"] = scores[0]["cause"] if scores else "待人工判断"
        merged["secondary_causes"] = [x["cause"] for x in scores[1:3]]
        result.append(merged)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="投诉根因打分脚本")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        records = json.load(f)

    results = analyze_records(records)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
