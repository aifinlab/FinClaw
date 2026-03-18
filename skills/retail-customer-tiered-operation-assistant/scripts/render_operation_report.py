#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import List, Dict


def render_report(items: List[Dict], objective: str = "零售客户分层经营") -> str:
    lines = []
    lines.append("# 零售客户分层经营报告")
    lines.append("")
    lines.append("## 一、经营目标与客户概况")
    lines.append(f"- 经营目标：{objective}")
    lines.append(f"- 客户数量：{len(items)}")
    lines.append("")
    lines.append("## 二、客户分层结果")
    lines.append("| 客户标识 | 层级 | 总分 | 经营目标 | 推荐渠道 |")
    lines.append("|---|---:|---:|---|---|")
    for item in items:
        channels = "、".join(item.get("推荐渠道", []))
        lines.append(f"| {item.get('客户标识','')} | {item.get('层级','')} | {item.get('总分','')} | {item.get('经营目标','')} | {channels} |")
    lines.append("")
    lines.append("## 三、经营优先级与策略建议")
    for item in items[:10]:
        lines.append(f"### {item.get('优先级','')}. {item.get('客户标识','')}")
        lines.append(f"- 层级：{item.get('层级','')}")
        lines.append(f"- 经营目标：{item.get('经营目标','')}")
        lines.append(f"- 推荐动作：{'、'.join(item.get('推荐动作', []))}")
        lines.append(f"- 推荐渠道：{'、'.join(item.get('推荐渠道', []))}")
    lines.append("")
    lines.append("## 四、风险提示与合规说明")
    lines.append("- 实际经营前应核验客户授权、适当性和频控要求。")
    lines.append("- 对投诉客户、老年客户和敏感客群应审慎触达。")
    lines.append("")
    lines.append("## 五、待补充信息与下一步动作")
    lines.append("- 补充近 90 天资产变动、交易活跃度和最近触达反馈。")
    return "
".join(lines)


if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    if isinstance(data, dict):
        data = [data]
    print(render_report(data))
