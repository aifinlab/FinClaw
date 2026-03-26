#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
账户流水核验报告生成脚本

用法:
  python flow_validation_report.py --input assets/flows.json --format markdown --output outputs/flow_validation.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json


@dataclass
class CashFlowRecord:
    account: str
    amount: float
    date: str
    counterparty: str
    direction: str


@dataclass
class ValidationPayload:
    accounts: List[str] = field(default_factory=list)
    cash_flows: List[CashFlowRecord] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    period: str = ""
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


DEFAULT_RULES = {
    "large_amount_threshold": 500000,
    "high_frequency_threshold": 50,
}


def parse_cash_flows(raw: List[Dict[str, Any]]) -> List[CashFlowRecord]:
    flows: List[CashFlowRecord] = []
    for item in raw:
        flows.append(
            CashFlowRecord(
                account=str(item.get("account", "")),
                amount=float(item.get("amount", 0)),
                date=str(item.get("date", "")),
                counterparty=str(item.get("counterparty", "")),
                direction=str(item.get("direction", "")),
            )
        )
    return flows


def parse_payload(raw: Dict[str, Any]) -> ValidationPayload:
    return ValidationPayload(
        accounts=list(raw.get("accounts", []) or []),
        cash_flows=parse_cash_flows(raw.get("cash_flows", []) or []),
        rules=dict(raw.get("rules", {}) or {}),
        period=str(raw.get("period", "")),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def summarize_flows(flows: List[CashFlowRecord], rules: Dict[str, Any]) -> Dict[str, Any]:
    large_threshold = float(rules["large_amount_threshold"])
    high_freq_threshold = int(rules["high_frequency_threshold"])

    large_transactions = [item for item in flows if abs(item.amount) >= large_threshold]
    counterparty_counts: Dict[str, int] = {}
    for item in flows:
        counterparty_counts[item.counterparty] = counterparty_counts.get(item.counterparty, 0) + 1

    high_freq_counterparties = [
        name for name, count in counterparty_counts.items() if count >= high_freq_threshold
    ]

    return {
        "total_amount": sum(item.amount for item in flows),
        "large_transactions": large_transactions,
        "high_freq_counterparties": high_freq_counterparties,
        "counterparty_counts": counterparty_counts,
    }


def build_markdown(payload: ValidationPayload) -> str:
    rules = {**DEFAULT_RULES, **payload.rules}
    summary = summarize_flows(payload.cash_flows, rules)

    lines: List[str] = []
    lines.append("# 账户流水核验报告")
    lines.append("")
    lines.append("## 流水覆盖度概览")
    lines.append(f"- 账户清单: {' / '.join(payload.accounts) if payload.accounts else '待补充'}")
    lines.append(f"- 样本期间: {payload.period or '待补充'}")
    lines.append(f"- 流水笔数: {len(payload.cash_flows)}")
    lines.append("")

    lines.append("## 核验结论")
    if summary["large_transactions"] or summary["high_freq_counterparties"]:
        lines.append("- 结论等级: 重点关注")
    else:
        lines.append("- 结论等级: 正常")
    lines.append("")

    lines.append("## 异常项清单")
    if summary["large_transactions"]:
        lines.append("### 大额交易")
        for item in summary["large_transactions"][:10]:
            lines.append(
                f"- {item.date} | {item.account} | {item.counterparty} | {item.direction} | {item.amount:,.2f}"
            )
    if summary["high_freq_counterparties"]:
        lines.append("### 高频对手方")
        for name in summary["high_freq_counterparties"]:
            lines.append(f"- {name}: {summary['counterparty_counts'][name]} 笔")
    if not summary["large_transactions"] and not summary["high_freq_counterparties"]:
        lines.append("- 暂无")
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


def build_json(payload: ValidationPayload) -> Dict[str, Any]:
    rules = {**DEFAULT_RULES, **payload.rules}
    summary = summarize_flows(payload.cash_flows, rules)
    return {
        "accounts": payload.accounts,
        "period": payload.period,
        "summary": {
            "total_amount": summary["total_amount"],
            "large_transactions": [item.__dict__ for item in summary["large_transactions"]],
            "high_freq_counterparties": summary["high_freq_counterparties"],
        },
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
    parser = argparse.ArgumentParser(description="账户流水核验报告生成脚本")
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
