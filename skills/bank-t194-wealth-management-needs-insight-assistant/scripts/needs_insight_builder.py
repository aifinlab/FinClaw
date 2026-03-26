#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
需求洞察诊断草稿生成器
- 输入: JSON 文件
- 输出: Markdown 报告草稿

用法:
python scripts/needs_insight_builder.py --input input.json --output report.md
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import json


REQUIRED_SECTIONS = {
    "customer": "客户信息",
    "products": "产品与市场",
    "context": "沟通背景",
    "metrics": "指标与数据",
    "events": "事件信息",
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _get_section(data: Dict[str, Any], key: str) -> Any:
    return data.get(key, {})


def _list_items(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            if isinstance(v, list):
                v_text = ", ".join([str(i) for i in v if str(i).strip()])
            else:
                v_text = str(v)
            items.append(f"{k}: {v_text}")
        return [item for item in items if item.strip()]
    return [str(value)]


def _format_bullets(items: List[str], empty_placeholder: str = "- 【待补充】") -> str:
    if not items:
        return empty_placeholder
    return "\n".join([f"- {item}" for item in items])


def _build_fact_section(data: Dict[str, Any]) -> str:
    blocks = []
    for key, title in REQUIRED_SECTIONS.items():
        items = _list_items(_get_section(data, key))
        blocks.append(f"### {title}\n{_format_bullets(items)}")
    return "\n\n".join(blocks)


def _build_drivers(data: Dict[str, Any]) -> Tuple[str, str, str]:
    drivers = data.get("drivers", {})
    main_drivers = _list_items(drivers.get("main"))
    secondary_drivers = _list_items(drivers.get("secondary"))
    uncertain_drivers = _list_items(drivers.get("uncertain"))
    return (
        _format_bullets(main_drivers),
        _format_bullets(secondary_drivers),
        _format_bullets(uncertain_drivers, empty_placeholder="- 【待确认】"),
    )


def _build_actions(data: Dict[str, Any]) -> Dict[str, str]:
    actions = data.get("actions", {})
    return {
        "配置或适配提示": _format_bullets(_list_items(actions.get("allocation"))),
        "沟通要点": _format_bullets(_list_items(actions.get("communication"))),
        "风险提示": _format_bullets(_list_items(actions.get("risk"))),
        "后续追问清单": _format_bullets(_list_items(actions.get("follow_up")), empty_placeholder="- 【待补充】"),
    }


def build_report(data: Dict[str, Any]) -> str:
    title = data.get("title", "需求洞察诊断草稿")
    report_date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    summary = _format_bullets(_list_items(data.get("summary")), empty_placeholder="- 【待补充】")

    facts = _build_fact_section(data)
    main_drivers, secondary_drivers, uncertain_drivers = _build_drivers(data)
    actions = _build_actions(data)

    missing = _format_bullets(_list_items(data.get("missing")), empty_placeholder="- 【待补充】")

    return (
        f"# {title}\n\n"
        f"- 日期: {report_date}\n"
        f"- 客户/对象: {data.get('client', '【待补充】')}\n"
        f"- 诊断范围: {data.get('scope', '【待补充】')}\n\n"
        "## 诊断摘要\n"
        f"{summary}\n\n"
        "## 事实层整理\n"
        f"{facts}\n\n"
        "## 驱动项拆解\n"
        "### 主驱动\n"
        f"{main_drivers}\n\n"
        "### 次驱动\n"
        f"{secondary_drivers}\n\n"
        "### 待确认驱动\n"
        f"{uncertain_drivers}\n\n"
        "## 业务动作与沟通建议\n"
        "### 配置或适配提示\n"
        f"{actions['配置或适配提示']}\n\n"
        "### 沟通要点\n"
        f"{actions['沟通要点']}\n\n"
        "### 风险提示\n"
        f"{actions['风险提示']}\n\n"
        "### 后续追问清单\n"
        f"{actions['后续追问清单']}\n\n"
        "## 缺失信息与待核验\n"
        f"{missing}\n"
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="需求洞察诊断草稿生成器")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件路径")
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = _load_json(input_path)
    report = build_report(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
