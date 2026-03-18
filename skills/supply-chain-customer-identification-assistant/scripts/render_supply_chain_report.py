#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""将供应链客户识别结果渲染为中文 Markdown 报告。"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List


def render(data: Dict[str, Any]) -> str:
    core = data.get("核心企业", "")
    customers: List[Dict[str, Any]] = data.get("客户列表", [])
    lines = [
        "# 供应链客户识别报告",
        "",
        "## 一、任务背景",
        f"- 核心企业：{core}",
        f"- 分析目的：{data.get('分析目的', '')}",
        f"- 分析范围：{data.get('分析范围', '')}",
        "",
        "## 二、客户识别结果",
        "",
    ]
    for idx, c in enumerate(customers, 1):
        lines.extend([
            f"### {idx}. {c.get('客户名称', '')}",
            f"- 客户角色：{c.get('客户角色', '')}",
            f"- 合作稳定性：{c.get('合作稳定性', '')}",
            f"- 交易闭环状态：{c.get('交易闭环状态', '')}",
            f"- 风险标签：{', '.join(c.get('风险标签', [])) if c.get('风险标签') else '无'}",
            f"- 初筛建议：{c.get('初筛建议', '')}",
            "",
        ])
    lines.extend([
        "## 三、整体风险提示",
        *(f"- {x}" for x in data.get("整体风险提示", [])),
        "",
        "## 四、待核验事项",
        *(f"- {x}" for x in data.get("待核验事项", [])),
        "",
        "## 五、结论摘要",
        f"- {data.get('结论摘要', '')}",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    payload = json.load(sys.stdin)
    sys.stdout.write(render(payload))


if __name__ == "__main__":
    main()
