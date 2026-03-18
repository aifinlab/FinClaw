#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
供应链融资匹配方案生成脚本

用法:
  python supply_chain_financing_matcher.py --input assets/supply_chain.json --format markdown --output outputs/financing_match.md
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SupplyChainNode:
    name: str
    role: str
    share: str


@dataclass
class FinancingProduct:
    name: str
    limit: str
    term: str
    requirements: List[str] = field(default_factory=list)


@dataclass
class FinancingPayload:
    core_enterprise: Dict[str, Any] = field(default_factory=dict)
    trade_loop: Dict[str, Any] = field(default_factory=dict)
    receivables: List[Dict[str, Any]] = field(default_factory=list)
    product_catalog: List[FinancingProduct] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


def parse_payload(raw: Dict[str, Any]) -> FinancingPayload:
    products_raw = raw.get("product_catalog", [])
    products: List[FinancingProduct] = []
    for item in products_raw:
        products.append(
            FinancingProduct(
                name=str(item.get("name", "")),
                limit=str(item.get("limit", "")),
                term=str(item.get("term", "")),
                requirements=list(item.get("requirements", []) or []),
            )
        )

    return FinancingPayload(
        core_enterprise=dict(raw.get("core_enterprise", {}) or {}),
        trade_loop=dict(raw.get("trade_loop", {}) or {}),
        receivables=list(raw.get("receivables", []) or []),
        product_catalog=products,
        rules=dict(raw.get("rules", {}) or {}),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def score_trade_loop(trade_loop: Dict[str, Any]) -> int:
    score = 0
    if trade_loop.get("orders"):
        score += 1
    if trade_loop.get("logistics"):
        score += 1
    if trade_loop.get("invoices"):
        score += 1
    if trade_loop.get("acceptance"):
        score += 1
    return score


def build_match_matrix(payload: FinancingPayload) -> List[Dict[str, Any]]:
    matrix: List[Dict[str, Any]] = []
    trade_score = score_trade_loop(payload.trade_loop)
    for product in payload.product_catalog:
        suitability = "高" if trade_score >= 3 else "中"
        matrix.append(
            {
                "product": product.name,
                "limit": product.limit,
                "term": product.term,
                "suitability": suitability,
                "requirements": product.requirements,
            }
        )
    return matrix


def build_markdown(payload: FinancingPayload) -> str:
    matrix = build_match_matrix(payload)

    lines: List[str] = []
    lines.append("# 供应链融资匹配方案")
    lines.append("")
    lines.append("## 核心企业画像")
    if payload.core_enterprise:
        for key, value in payload.core_enterprise.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 待补充核心企业信息")
    lines.append("")

    lines.append("## 贸易闭环")
    if payload.trade_loop:
        for key, value in payload.trade_loop.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 待补充贸易闭环信息")
    lines.append("")

    lines.append("## 融资匹配矩阵")
    if matrix:
        for item in matrix:
            lines.append(
                f"- {item['product']}: 额度 {item['limit']} / 期限 {item['term']} / 匹配度 {item['suitability']}"
            )
    else:
        lines.append("- 暂无可匹配产品")
    lines.append("")

    lines.append("## 风险提示")
    lines.append("- 关注应收账款真实性与账龄结构")
    lines.append("- 关注核心企业付款记录")
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


def build_json(payload: FinancingPayload) -> Dict[str, Any]:
    return {
        "core_enterprise": payload.core_enterprise,
        "trade_loop": payload.trade_loop,
        "receivables": payload.receivables,
        "match_matrix": build_match_matrix(payload),
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
    parser = argparse.ArgumentParser(description="供应链融资匹配方案生成脚本")
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
