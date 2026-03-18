#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
普惠税票/流水数据核验报告生成脚本

用法:
  python data_validation_report.py --input assets/tax_flow.json --format markdown --output outputs/data_validation.md
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class InvoiceRecord:
    invoice_no: str
    amount: float
    date: str
    buyer: str


@dataclass
class CashFlowRecord:
    account: str
    amount: float
    date: str
    counterparty: str
    direction: str


@dataclass
class ValidationPayload:
    invoice_records: List[InvoiceRecord] = field(default_factory=list)
    tax_declarations: List[Dict[str, Any]] = field(default_factory=list)
    cash_flows: List[CashFlowRecord] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    period: str = ""
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


DEFAULT_RULES = {
    "invoice_amount_gap_ratio": 0.3,
    "cash_flow_gap_ratio": 0.35,
    "min_invoice_count": 3,
}


def parse_invoices(raw: List[Dict[str, Any]]) -> List[InvoiceRecord]:
    invoices: List[InvoiceRecord] = []
    for item in raw:
        invoices.append(
            InvoiceRecord(
                invoice_no=str(item.get("invoice_no", "")),
                amount=float(item.get("amount", 0)),
                date=str(item.get("date", "")),
                buyer=str(item.get("buyer", "")),
            )
        )
    return invoices


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
        invoice_records=parse_invoices(raw.get("invoice_records", []) or []),
        tax_declarations=list(raw.get("tax_declarations", []) or []),
        cash_flows=parse_cash_flows(raw.get("cash_flows", []) or []),
        rules=dict(raw.get("rules", {}) or {}),
        period=str(raw.get("period", "")),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def calc_total_amount(records: List[InvoiceRecord]) -> float:
    return sum(item.amount for item in records)


def calc_flow_amount(records: List[CashFlowRecord]) -> float:
    return sum(item.amount for item in records)


def build_markdown(payload: ValidationPayload) -> str:
    rules = {**DEFAULT_RULES, **payload.rules}
    invoice_total = calc_total_amount(payload.invoice_records)
    flow_total = calc_flow_amount(payload.cash_flows)
    tax_total = sum(float(item.get("declared_amount", 0)) for item in payload.tax_declarations)

    invoice_gap_ratio = abs(invoice_total - tax_total) / tax_total if tax_total else 0
    cash_gap_ratio = abs(flow_total - tax_total) / tax_total if tax_total else 0

    lines: List[str] = []
    lines.append("# 税票/流水数据核验报告")
    lines.append("")
    lines.append("## 数据概览")
    lines.append(f"- 样本期间: {payload.period or '待补充'}")
    lines.append(f"- 发票数量: {len(payload.invoice_records)}")
    lines.append(f"- 流水笔数: {len(payload.cash_flows)}")
    lines.append(f"- 纳税申报次数: {len(payload.tax_declarations)}")
    lines.append("")

    lines.append("## 核验结论")
    issue_flags = []
    if len(payload.invoice_records) < rules["min_invoice_count"]:
        issue_flags.append("发票数量偏少")
    if invoice_gap_ratio > rules["invoice_amount_gap_ratio"]:
        issue_flags.append("发票与申报金额差异偏大")
    if cash_gap_ratio > rules["cash_flow_gap_ratio"]:
        issue_flags.append("流水与申报金额差异偏大")

    if issue_flags:
        lines.append("- 结论等级: 重点关注")
        for flag in issue_flags:
            lines.append(f"- {flag}")
    else:
        lines.append("- 结论等级: 正常")
        lines.append("- 未发现显著异常")
    lines.append("")

    lines.append("## 经营真实性判断")
    lines.append(f"- 发票总额: {invoice_total:,.2f}")
    lines.append(f"- 纳税申报总额: {tax_total:,.2f}")
    lines.append(f"- 流水总额: {flow_total:,.2f}")
    lines.append(f"- 发票/申报差异比例: {invoice_gap_ratio:.2%}")
    lines.append(f"- 流水/申报差异比例: {cash_gap_ratio:.2%}")
    lines.append("")

    lines.append("## 异常项清单")
    if issue_flags:
        for flag in issue_flags:
            lines.append(f"- {flag}")
    else:
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
    invoice_total = calc_total_amount(payload.invoice_records)
    flow_total = calc_flow_amount(payload.cash_flows)
    tax_total = sum(float(item.get("declared_amount", 0)) for item in payload.tax_declarations)

    return {
        "period": payload.period,
        "totals": {
            "invoice_total": invoice_total,
            "tax_total": tax_total,
            "cash_flow_total": flow_total,
        },
        "rules": rules,
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
    parser = argparse.ArgumentParser(description="普惠税票/流水数据核验报告生成脚本")
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
