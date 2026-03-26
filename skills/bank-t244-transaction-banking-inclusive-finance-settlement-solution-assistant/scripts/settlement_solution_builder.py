#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
普惠结算方案生成脚本

用法:
  python settlement_solution_builder.py --input assets/settlement_input.json --format markdown --output outputs/settlement_solution.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json


@dataclass
class SettlementOption:
    name: str
    scenario: str
    advantages: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class SettlementPayload:
    client_profile: Dict[str, Any] = field(default_factory=dict)
    settlement_needs: Dict[str, Any] = field(default_factory=dict)
    options: List[SettlementOption] = field(default_factory=list)
    risk_notes: List[str] = field(default_factory=list)
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


def parse_payload(raw: Dict[str, Any]) -> SettlementPayload:
    options_raw = raw.get("options", [])
    options: List[SettlementOption] = []
    for item in options_raw:
        options.append(
            SettlementOption(
                name=str(item.get("name", "")),
                scenario=str(item.get("scenario", "")),
                advantages=list(item.get("advantages", []) or []),
                constraints=list(item.get("constraints", []) or []),
            )
        )

    return SettlementPayload(
        client_profile=dict(raw.get("client_profile", {}) or {}),
        settlement_needs=dict(raw.get("settlement_needs", {}) or {}),
        options=options,
        risk_notes=list(raw.get("risk_notes", []) or []),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def build_markdown(payload: SettlementPayload) -> str:
    lines: List[str] = []
    lines.append("# 普惠结算方案建议")
    lines.append("")
    lines.append("## 客户概览")
    for key, value in payload.client_profile.items():
        lines.append(f"- {key}: {value}")
    if not payload.client_profile:
        lines.append("- 待补充客户画像")
    lines.append("")

    lines.append("## 结算需求")
    for key, value in payload.settlement_needs.items():
        lines.append(f"- {key}: {value}")
    if not payload.settlement_needs:
        lines.append("- 待补充结算需求")
    lines.append("")

    lines.append("## 主方案")
    if payload.options:
        main_option = payload.options[0]
        lines.append(f"- 方案: {main_option.name}")
        lines.append(f"- 适用场景: {main_option.scenario}")
        if main_option.advantages:
            lines.append("- 优势: " + " / ".join(main_option.advantages))
        if main_option.constraints:
            lines.append("- 限制条件: " + " / ".join(main_option.constraints))
    else:
        lines.append("- 暂无方案")
    lines.append("")

    lines.append("## 备选方案")
    if len(payload.options) > 1:
        for option in payload.options[1:3]:
            lines.append(f"- {option.name}: {option.scenario}")
    else:
        lines.append("- 暂无备选方案")
    lines.append("")

    lines.append("## 风险提示")
    if payload.risk_notes:
        for note in payload.risk_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- 待补充风险提示")
    lines.append("")

    lines.append("## 待核验信息")
    if payload.to_verify:
        for item in payload.to_verify:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")
    lines.append("")

    lines.append("## 已确认信息")
    if payload.confirmed:
        for item in payload.confirmed:
            lines.append(f"- {item}")
    else:
        lines.append("- 待补充")
    lines.append("")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(lines)


def build_json(payload: SettlementPayload) -> Dict[str, Any]:
    return {
        "client_profile": payload.client_profile,
        "settlement_needs": payload.settlement_needs,
        "options": [item.__dict__ for item in payload.options],
        "risk_notes": payload.risk_notes,
        "confirmed": payload.confirmed,
        "to_verify": payload.to_verify,
        "generated_at": datetime.now().isoformat(timespec="minutes"),
    }


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, content: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="普惠结算方案生成脚本")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", required=True, help="输出文件路径")
    args = parser.parse_args()

    payload = parse_payload(read_json(Path(args.input)))
    if args.format == "json":
        write_json(Path(args.output), build_json(payload))
    else:
        write_output(Path(args.output), build_markdown(payload))


if __name__ == "__main__":
    main()
