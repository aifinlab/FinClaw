#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将结构化校验结果渲染为 Markdown 报告。"""

from __future__ import annotations
from typing import Any, Dict, List
import json
import sys


def render(payload: Dict[str, Any]) -> str:
    bg = payload.get("task_background", {})
    issues: List[Dict[str, Any]] = payload.get("issues", [])
    lines = []
    lines.append("# 监管报送校验报告")
    lines.append("")
    lines.append("## 一、任务背景")
    lines.append(f"- 报表名称：{bg.get('report_name', '')}")
    lines.append(f"- 报送期次：{bg.get('period', '')}")
    lines.append(f"- 校验范围：{bg.get('scope', '')}")
    lines.append("")
    lines.append("## 二、总体结论")
    lines.append(payload.get("overall_conclusion", ""))
    lines.append("")
    lines.append("## 三、关键问题清单")
    lines.append("| 问题编号 | 字段/指标 | 问题类型 | 严重程度 | 发现依据 | 状态 |")
    lines.append("|---|---|---|---|---|---|")
    for x in issues:
        lines.append(
            f"| {x.get('issue_id','')} | {x.get('field','')} | {x.get('issue_type','')} | {x.get('severity','')} | {x.get('evidence','')} | {x.get('status','')} |"
        )
    lines.append("")
    lines.append("## 四、待核验事项")
    for item in payload.get("pending_items", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 五、整改建议")
    for item in payload.get("rectification_actions", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 六、结论边界")
    lines.append(payload.get("boundary_note", ""))
    return "\n".join(lines)


def main() -> None:
    payload = json.load(sys.stdin)
    sys.stdout.write(render(payload))


if __name__ == "__main__":
    main()
