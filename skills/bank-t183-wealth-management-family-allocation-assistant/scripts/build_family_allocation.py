#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
家庭资产配置建议生成器

输入: JSON 文件
输出: Markdown 或 JSON 报告

示例:
  python build_family_allocation.py --input sample.json --output plan.md
  python build_family_allocation.py --input sample.json --format json
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


RISK_BUCKETS = {
    "保守": {
        "liquidity": (0.20, 0.35),
        "income": (0.35, 0.50),
        "growth": (0.15, 0.25),
        "protection": (0.05, 0.10),
    },
    "稳健": {
        "liquidity": (0.15, 0.25),
        "income": (0.30, 0.45),
        "growth": (0.20, 0.30),
        "protection": (0.05, 0.10),
    },
    "均衡": {
        "liquidity": (0.10, 0.20),
        "income": (0.25, 0.40),
        "growth": (0.25, 0.40),
        "protection": (0.05, 0.10),
    },
    "进取": {
        "liquidity": (0.08, 0.15),
        "income": (0.15, 0.30),
        "growth": (0.45, 0.60),
        "protection": (0.03, 0.08),
    },
}


@dataclass
class FamilyInput:
    name: str = "客户家庭"
    risk_level: str = "稳健"
    horizon_years: Optional[int] = None
    liquidity_months: Optional[int] = None
    total_assets: Optional[float] = None
    monthly_expense: Optional[float] = None
    goals: List[Dict[str, Any]] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    holdings: List[Dict[str, Any]] = field(default_factory=list)
    product_pool: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def load_input(path: str) -> FamilyInput:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return FamilyInput(
        name=raw.get("name", "客户家庭"),
        risk_level=raw.get("risk_level", "稳健"),
        horizon_years=raw.get("horizon_years"),
        liquidity_months=raw.get("liquidity_months"),
        total_assets=_safe_float(raw.get("total_assets")),
        monthly_expense=_safe_float(raw.get("monthly_expense")),
        goals=raw.get("goals", []),
        constraints=raw.get("constraints", {}),
        holdings=raw.get("holdings", []),
        product_pool=raw.get("product_pool", []),
        notes=raw.get("notes", []),
    )


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        return weights
    return {k: v / total for k, v in weights.items()}


def derive_liquidity_need(data: FamilyInput) -> Optional[float]:
    if data.liquidity_months and data.monthly_expense:
        return data.liquidity_months * data.monthly_expense
    return None


def build_allocation(data: FamilyInput) -> Tuple[Dict[str, float], List[str], List[str]]:
    warnings: List[str] = []
    assumptions: List[str] = []

    base = RISK_BUCKETS.get(data.risk_level, RISK_BUCKETS["稳健"])
    weights = {k: (v[0] + v[1]) / 2 for k, v in base.items()}

    liquidity_need = derive_liquidity_need(data)
    if liquidity_need and data.total_assets:
        liquidity_ratio = liquidity_need / data.total_assets
        if liquidity_ratio > weights["liquidity"]:
            assumptions.append(
                f"按流动性需求估算，建议流动性占比上调至约 {liquidity_ratio:.0%}。"
            )
            weights["liquidity"] = clamp(liquidity_ratio, base["liquidity"][0], 0.5)

    horizon = data.horizon_years
    if horizon is not None:
        if horizon <= 2:
            weights["growth"] = max(weights["growth"] - 0.05, 0.05)
            weights["income"] = min(weights["income"] + 0.03, 0.6)
            weights["liquidity"] = min(weights["liquidity"] + 0.02, 0.5)
            assumptions.append("短期限目标存在，降低增长型比例、提高流动性与稳健收益比重。")
        elif horizon >= 8:
            weights["growth"] = min(weights["growth"] + 0.05, 0.65)
            weights["income"] = max(weights["income"] - 0.03, 0.1)
            assumptions.append("长期目标占比高，适度提升增长型配置比例。")

    constraints = data.constraints or {}
    min_liquidity = _safe_float(constraints.get("min_liquidity_ratio"))
    max_growth = _safe_float(constraints.get("max_growth_ratio"))

    if min_liquidity is not None and min_liquidity > weights["liquidity"]:
        weights["liquidity"] = clamp(min_liquidity, 0.05, 0.6)
        assumptions.append("根据约束条件，提高流动性比例以满足最低要求。")

    if max_growth is not None and max_growth < weights["growth"]:
        weights["growth"] = clamp(max_growth, 0.05, 0.6)
        assumptions.append("根据约束条件，限制增长型资产比例。")

    weights = normalize_weights(weights)

    if data.total_assets is None:
        warnings.append("未提供总资产规模，输出仅给出比例建议。")
    if data.risk_level not in RISK_BUCKETS:
        warnings.append("风险等级未在预设范围内，已按“稳健”口径处理。")
    if not data.goals:
        warnings.append("未提供明确目标清单，需补充目标优先级与期限。")

    return weights, warnings, assumptions


def format_markdown(
    data: FamilyInput, weights: Dict[str, float], warnings: List[str], assumptions: List[str]
) -> str:
    lines: List[str] = []
    lines.append(f"# {data.name} 家庭资产配置建议（草案）")
    lines.append("")
    lines.append("## 关键结论")
    lines.append(
        f"- 风险等级口径：{data.risk_level}；建议配置比例为流动性 {weights['liquidity']:.0%}、稳健收益 {weights['income']:.0%}、增长型 {weights['growth']:.0%}、保障型 {weights['protection']:.0%}"
    )
    if data.horizon_years is not None:
        lines.append(f"- 目标期限：{data.horizon_years} 年")
    if data.total_assets:
        lines.append(f"- 资产规模：约 {data.total_assets:,.0f}")
    lines.append("")

    lines.append("## 配置思路")
    lines.append("- 以家庭现金流安全垫为底，满足短期支出与备用金需求。")
    lines.append("- 以稳健收益型资产覆盖中期目标并平滑波动。")
    lines.append("- 以增长型资产承接长期目标与通胀对冲需求。")
    lines.append("- 保障型资产用于重大风险事件的对冲与家庭责任覆盖。")
    lines.append("")

    lines.append("## 配置建议（比例）")
    lines.append(f"- 流动性：{weights['liquidity']:.0%}")
    lines.append(f"- 稳健收益：{weights['income']:.0%}")
    lines.append(f"- 增长型：{weights['growth']:.0%}")
    lines.append(f"- 保障型：{weights['protection']:.0%}")
    lines.append("")

    if data.total_assets:
        lines.append("## 配置建议（金额）")
        lines.append(f"- 流动性：约 {data.total_assets * weights['liquidity']:,.0f}")
        lines.append(f"- 稳健收益：约 {data.total_assets * weights['income']:,.0f}")
        lines.append(f"- 增长型：约 {data.total_assets * weights['growth']:,.0f}")
        lines.append(f"- 保障型：约 {data.total_assets * weights['protection']:,.0f}")
        lines.append("")

    if data.goals:
        lines.append("## 目标清单")
        for goal in data.goals:
            name = goal.get("name", "目标")
            amount = goal.get("amount")
            horizon = goal.get("horizon_years")
            line = f"- {name}"
            if amount is not None:
                line += f"：资金需求 {amount}"
            if horizon is not None:
                line += f"，期限 {horizon} 年"
            lines.append(line)
        lines.append("")

    if assumptions:
        lines.append("## 关键假设")
        lines.extend([f"- {item}" for item in assumptions])
        lines.append("")

    if warnings:
        lines.append("## 待补充事项")
        lines.extend([f"- {item}" for item in warnings])
        lines.append("")

    lines.append("## 沟通要点")
    lines.append("- 说明配置比例来源于风险等级与期限匹配，不代表收益承诺。")
    lines.append("- 明确资金用途与流动性边界，避免因短期需求破坏长期配置。")
    lines.append("- 建议定期复核（至少半年一次）并根据家庭事件动态调整。")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="家庭资产配置建议生成器")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    data = load_input(args.input)
    weights, warnings, assumptions = build_allocation(data)

    if args.format == "json":
        payload = {
            "name": data.name,
            "risk_level": data.risk_level,
            "weights": weights,
            "assumptions": assumptions,
            "warnings": warnings,
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        content = format_markdown(data, weights, warnings, assumptions)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)


if __name__ == "__main__":
    main()
