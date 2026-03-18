#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
普惠产品推荐方案生成脚本

用法:
  python product_recommendation_builder.py --input assets/product_input.json --format markdown --output outputs/product_recommendation.md
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ProductItem:
    name: str
    category: str
    limit: str
    term: str
    rate: str
    requirements: List[str] = field(default_factory=list)


@dataclass
class RecommendationPayload:
    client_profile: Dict[str, Any] = field(default_factory=dict)
    demand: Dict[str, Any] = field(default_factory=dict)
    products: List[ProductItem] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    confirmed: List[str] = field(default_factory=list)
    to_verify: List[str] = field(default_factory=list)


def parse_payload(raw: Dict[str, Any]) -> RecommendationPayload:
    products_raw = raw.get("products", [])
    products: List[ProductItem] = []
    for item in products_raw:
        products.append(
            ProductItem(
                name=str(item.get("name", "")),
                category=str(item.get("category", "")),
                limit=str(item.get("limit", "")),
                term=str(item.get("term", "")),
                rate=str(item.get("rate", "")),
                requirements=list(item.get("requirements", []) or []),
            )
        )

    return RecommendationPayload(
        client_profile=dict(raw.get("client_profile", {}) or {}),
        demand=dict(raw.get("demand", {}) or {}),
        products=products,
        constraints=list(raw.get("constraints", []) or []),
        confirmed=list(raw.get("confirmed", []) or []),
        to_verify=list(raw.get("to_verify", []) or []),
    )


def match_products(payload: RecommendationPayload) -> List[ProductItem]:
    if not payload.products:
        return []
    target_purpose = str(payload.demand.get("purpose", "")).lower()
    matches: List[ProductItem] = []
    for product in payload.products:
        if target_purpose and target_purpose not in product.category.lower():
            matches.append(product)
        else:
            matches.append(product)
    return matches


def build_markdown(payload: RecommendationPayload) -> str:
    matches = match_products(payload)

    lines: List[str] = []
    lines.append("# 普惠产品推荐方案")
    lines.append("")
    lines.append("## 客户概览")
    for key, value in payload.client_profile.items():
        lines.append(f"- {key}: {value}")
    if not payload.client_profile:
        lines.append("- 待补充客户画像")
    lines.append("")

    lines.append("## 需求概览")
    for key, value in payload.demand.items():
        lines.append(f"- {key}: {value}")
    if not payload.demand:
        lines.append("- 待补充需求")
    lines.append("")

    lines.append("## 主推荐方案")
    if matches:
        main_product = matches[0]
        lines.append(f"- 产品: {main_product.name} ({main_product.category})")
        lines.append(f"- 额度: {main_product.limit}")
        lines.append(f"- 期限: {main_product.term}")
        lines.append(f"- 利率/费率: {main_product.rate}")
        if main_product.requirements:
            lines.append("- 准入要求: " + " / ".join(main_product.requirements))
    else:
        lines.append("- 暂无可推荐产品")
    lines.append("")

    lines.append("## 备选方案")
    if len(matches) > 1:
        for product in matches[1:3]:
            lines.append(
                f"- {product.name}: 额度 {product.limit} / 期限 {product.term} / 利率 {product.rate}"
            )
    else:
        lines.append("- 暂无备选方案")
    lines.append("")

    lines.append("## 约束与风险提示")
    if payload.constraints:
        for item in payload.constraints:
            lines.append(f"- {item}")
    else:
        lines.append("- 待补充约束条件")
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


def build_json(payload: RecommendationPayload) -> Dict[str, Any]:
    matches = match_products(payload)
    return {
        "client_profile": payload.client_profile,
        "demand": payload.demand,
        "recommendations": [item.__dict__ for item in matches],
        "constraints": payload.constraints,
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
    parser = argparse.ArgumentParser(description="普惠产品推荐方案生成脚本")
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
