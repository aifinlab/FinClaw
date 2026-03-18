#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
票据贴现核验报告生成脚本

用法:
  python bill_discount_report.py --input assets/bill_input.json --format markdown --output outputs/bill_discount.md
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class BillInfo:
    bill_type: str
    amount: float
    term: str
    acceptor: str


@dataclass
class EndorsementItem:
    node: str
    status: str


@dataclass
class BillPayload:
    bill_info: BillInfo = field(default_factory=lambda: BillInfo("", 0.0, "", ""))
    endorsement_chain: List[EndorsementItem] = field(default_factory=list)
    trade_docs: Dict[str, Any] = field(default_factory=dict)
    discount_terms: Dict[str, Any] = field(default_factory=dict)
    rules: Dict[str, Any] = field(default_factory=dict)
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


def parse_payload(raw: Dict[str, Any]) -> BillPayload:
    bill_raw = raw.get("bill_info", {})
    bill_info = BillInfo(
        bill_type=str(bill_raw.get("bill_type", "")),
        amount=float(bill_raw.get("amount", 0)),
        term=str(bill_raw.get("term", "")),
        acceptor=str(bill_raw.get("acceptor", "")),
    )

    chain_raw = raw.get("endorsement_chain", [])
    chain: List[EndorsementItem] = []
    for item in chain_raw:
        chain.append(
            EndorsementItem(
                node=str(item.get("node", "")),
                status=str(item.get("status", "")),
            )
        )

    return BillPayload(
        bill_info=bill_info,
        endorsement_chain=chain,
        trade_docs=dict(raw.get("trade_docs", {}) or {}),
        discount_terms=dict(raw.get("discount_terms", {}) or {}),
        rules=dict(raw.get("rules", {}) or {}),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def build_markdown(payload: BillPayload) -> str:
    lines: List[str] = []
    lines.append("# 票据贴现核验报告")
    lines.append("")
    lines.append("## 票据信息")
    lines.append(f"- 票据类型: {payload.bill_info.bill_type or '待补充'}")
    lines.append(f"- 金额: {payload.bill_info.amount:,.2f}")
    lines.append(f"- 期限: {payload.bill_info.term or '待补充'}")
    lines.append(f"- 承兑人: {payload.bill_info.acceptor or '待补充'}")
    lines.append("")

    lines.append("## 背书链条")
    if payload.endorsement_chain:
        for item in payload.endorsement_chain:
            lines.append(f"- {item.node}: {item.status}")
    else:
        lines.append("- 待补充背书链条")
    lines.append("")

    lines.append("## 贸易背景核验")
    if payload.trade_docs:
        for key, value in payload.trade_docs.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 待补充贸易背景材料")
    lines.append("")

    lines.append("## 贴现方案")
    if payload.discount_terms:
        for key, value in payload.discount_terms.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 待补充贴现条款")
    lines.append("")

    lines.append("## 风险提示")
    lines.append("- 核验票据真实性与承兑人资质")
    lines.append("- 检查背书链条完整性与贸易背景匹配度")
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


def build_json(payload: BillPayload) -> Dict[str, Any]:
    return {
        "bill_info": payload.bill_info.__dict__,
        "endorsement_chain": [item.__dict__ for item in payload.endorsement_chain],
        "trade_docs": payload.trade_docs,
        "discount_terms": payload.discount_terms,
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
    parser = argparse.ArgumentParser(description="票据贴现核验报告生成脚本")
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
