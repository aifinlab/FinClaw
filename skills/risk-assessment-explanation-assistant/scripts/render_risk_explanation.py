#!/usr/bin/env python3
"""风险测评解释助手 Markdown 渲染脚本。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TITLE = "风险测评解释助手"


def render_list(items: list[Any]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def render_markdown(payload: dict[str, Any]) -> str:
    return f"""# {TITLE}

## 一、结论摘要

{payload.get("summary", "待补充")}

## 二、关键发现

{render_list(payload.get("key_findings", []))}

## 三、风险提示

{render_list(payload.get("risks", []))}

## 四、缺失信息

{render_list(payload.get("missing_information", []))}

## 五、后续动作

{render_list(payload.get("recommended_actions", []))}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to structured JSON result.")
    parser.add_argument("--output", help="Optional markdown output path.")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    markdown = render_markdown(payload)
    if args.output:
        Path(args.output).write_text(markdown + "\n", encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
