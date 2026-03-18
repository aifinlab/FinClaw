#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
普惠现金管理方案生成脚本

用法:
  python cash_management_builder.py --input assets/cash_input.json --format markdown --output outputs/cash_management.md
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class CashFlowProfile:
    income_cycle: str
    expense_cycle: str
    peak_needs: str
    pooling_goal: str


@dataclass
class CashManagementPayload:
    cash_flow_profile: CashFlowProfile = field(default_factory=lambda: CashFlowProfile("", "", "", ""))
    account_structure: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


def parse_payload(raw: Dict[str, Any]) -> CashManagementPayload:
    profile_raw = raw.get("cash_flow_profile", {})
    profile = CashFlowProfile(
        income_cycle=str(profile_raw.get("income_cycle", "")),
        expense_cycle=str(profile_raw.get("expense_cycle", "")),
        peak_needs=str(profile_raw.get("peak_needs", "")),
        pooling_goal=str(profile_raw.get("pooling_goal", "")),
    )

    return CashManagementPayload(
        cash_flow_profile=profile,
        account_structure=dict(raw.get("account_structure", {}) or {}),
        constraints=list(raw.get("constraints", []) or []),
        targets=list(raw.get("targets", []) or []),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def build_markdown(payload: CashManagementPayload) -> str:
    lines: List[str] = []
    lines.append("# 普惠现金管理方案")
    lines.append("")
    lines.append("## 资金结构")
    lines.append(f"- 收入节奏: {payload.cash_flow_profile.income_cycle or '待补充'}")
    lines.append(f"- 支出节奏: {payload.cash_flow_profile.expense_cycle or '待补充'}")
    lines.append(f"- 资金峰值需求: {payload.cash_flow_profile.peak_needs or '待补充'}")
    lines.append(f"- 归集目标: {payload.cash_flow_profile.pooling_goal or '待补充'}")
    lines.append("")

    lines.append("## 账户体系")
    if payload.account_structure:
        for key, value in payload.account_structure.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 待补充账户结构")
    lines.append("")

    lines.append("## 主方案")
    lines.append("- 归集路径: 主账户 -> 子账户 -> 资金池")
    lines.append("- 头寸管理: 按日归集 + 高峰期临时头寸")
    lines.append("- 权限设置: 资金归集与支付权限分离")
    lines.append("")

    lines.append("## 备选方案")
    lines.append("- 方案二: 按区域归集 + 总账户轧差")
    lines.append("- 方案三: 票据池 + 资金池组合")
    lines.append("")

    lines.append("## 目标与约束")
    if payload.targets:
        lines.append("- 目标: " + " / ".join(payload.targets))
    else:
        lines.append("- 目标: 待补充")
    if payload.constraints:
        lines.append("- 约束: " + " / ".join(payload.constraints))
    else:
        lines.append("- 约束: 待补充")
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


def build_json(payload: CashManagementPayload) -> Dict[str, Any]:
    return {
        "cash_flow_profile": payload.cash_flow_profile.__dict__,
        "account_structure": payload.account_structure,
        "constraints": payload.constraints,
        "targets": payload.targets,
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
    parser = argparse.ArgumentParser(description="普惠现金管理方案生成脚本")
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
