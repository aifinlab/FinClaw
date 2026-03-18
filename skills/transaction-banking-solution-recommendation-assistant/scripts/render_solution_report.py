#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, List

def render_report(data: Dict) -> str:
    lines = []
    lines.append("# 交易银行方案推荐报告")
    lines.append("")
    lines.append("## 一、客户概况")
    lines.append(f"- 客户名称：{data.get('客户名称', '未提供')}")
    lines.append(f"- 所属行业：{data.get('所属行业', '未提供')}")
    lines.append(f"- 经营模式：{data.get('经营模式', '未提供')}")
    lines.append(f"- 主要诉求：{data.get('主要诉求', '未提供')}")
    lines.append("")
    lines.append("## 二、推荐方案总览")
    for idx, item in enumerate(data.get("推荐方案", []), 1):
        lines.append(f"### {idx}. {item.get('方案', '未命名方案')}")
        lines.append(f"- 匹配理由：{item.get('匹配理由', '未提供')}")
        lines.append(f"- 优先级：{item.get('优先级', '未提供')}")
        lines.append(f"- 依赖条件：{item.get('依赖条件', '未提供')}")
        lines.append("")

    lines.append("## 三、风险提示")
    for risk in data.get("风险提示", []):
        lines.append(f"- {risk}")

    lines.append("")
    lines.append("## 四、待补充信息")
    for gap in data.get("待补充信息", []):
        lines.append(f"- {gap}")

    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    print(render_report(data))
