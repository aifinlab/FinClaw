#!/usr/bin/env python3
"""Render a markdown due diligence report from structured JSON.

Usage:
    python render_dd_report.py input.json > report.md
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Iterable, List


def get_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def section_lines(title: str, body: Iterable[str]) -> List[str]:
    lines = [f"## {title}"]
    items = list(body)
    if not items:
        lines.append("待补充")
    else:
        lines.extend(items)
    lines.append("")
    return lines


def render(data: Dict[str, Any]) -> str:
    company = data.get("company_name", "未命名企业")
    lines: List[str] = [f"# {company} 授信尽调报告（草稿）", ""]

    lines += section_lines("一、任务目标", get_list(data.get("task_goal") or ["围绕企业授信申请开展基础尽职调查与风险识别。"]))
    lines += section_lines("二、客户基本情况", get_list(data.get("basic_info")))
    lines += section_lines("三、股权结构与实控情况", get_list(data.get("ownership")))
    lines += section_lines("四、经营情况分析", get_list(data.get("operations")))
    lines += section_lines("五、财务与偿债能力分析", get_list(data.get("financials")))
    lines += section_lines("六、授信用途与还款来源", get_list(data.get("funding_and_repayment")))
    lines += section_lines("七、增信措施分析", get_list(data.get("credit_enhancement")))
    lines += section_lines("八、主要风险点", [f"- {x}" for x in get_list(data.get("risks"))])
    lines += section_lines("九、待补充核查事项", [f"- {x}" for x in get_list(data.get("missing_items"))])
    lines += section_lines("十、初步结论", get_list(data.get("preliminary_view") or ["当前结论仅为初步判断，需以补充材料和进一步核验结果为准。"]))

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python render_dd_report.py input.json", file=sys.stderr)
        return 1

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        print("Input JSON must be an object.", file=sys.stderr)
        return 1

    print(render(data), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
