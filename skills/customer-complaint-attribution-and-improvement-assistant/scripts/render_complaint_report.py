#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
客诉分析报告渲染脚本
将输入 JSON 渲染为 Markdown 报告。
"""

from __future__ import annotations
import json
from typing import Any, Dict, List
import argparse


def render_record(item: Dict[str, Any], idx: int) -> str:
    lines = []
    lines.append(f"  # {idx}. 投诉记录")
    lines.append(f"- 标题：{item.get('title', '')}")
    lines.append(f"- 主分类：{item.get('main_category', '未分类')}")
    lines.append(f"- 次分类：{', '.join(item.get('sub_categories', [])) or '无'}")
    lines.append(f"- 主归因：{item.get('primary_cause', '待判断')}")
    lines.append(f"- 次归因：{', '.join(item.get('secondary_causes', [])) or '无'}")
    lines.append(f"- 客户诉求：{item.get('customer_request', '')}")
    lines.append(f"- 内容摘要：{item.get('summary', item.get('content', ''))}")
    lines.append("")
    lines.append("  # 已确认事实")
    for fact in item.get("confirmed_facts", []):
        lines.append(f"- {fact}")
    if not item.get("confirmed_facts"):
        lines.append("- 暂无")
    lines.append("")
    lines.append("  # 待核验事项")
    for pending in item.get("pending_checks", []):
        lines.append(f"- {pending}")
    if not item.get("pending_checks"):
        lines.append("- 暂无")
    lines.append("")
    lines.append("  # 改进建议")
    for action in item.get("actions", []):
        lines.append(f"- {action}")
    if not item.get("actions"):
        lines.append("- 建议结合具体证据补充人工判断")
    lines.append("")
    return "\n".join(lines)


def render_report(records: List[Dict[str, Any]]) -> str:
    parts = ["  # 客诉分析报告", ""]
    parts.append(f"投诉记录数量：{len(records)}")
    parts.append("")
    for i, item in enumerate(records, start=1):
        parts.append(render_record(item, i))
    return "\n".join(parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="客诉分析报告渲染脚本")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        records = json.load(f)

    report = render_report(records)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
