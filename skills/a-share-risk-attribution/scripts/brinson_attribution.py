#!/usr/bin/env python3
"""
Brinson 单期绩效归因 (Brinson-Fachler 模型)

输入: 组合各行业权重/收益, 基准各行业权重/收益
输出: 配置效应 / 选股效应 / 交互效应

用法:
    python brinson_attribution.py --portfolio portfolio.csv --benchmark benchmark.csv
    python brinson_attribution.py --json '{"portfolio": [...], "benchmark": [...]}'

CSV 格式:
    sector,weight,return
    银行,0.15,0.03
    医药,0.10,-0.02
    ...

JSON 格式:
    {
      "portfolio": [
        {"sector": "银行", "weight": 0.15, "return": 0.03},
        ...
      ],
      "benchmark": [
        {"sector": "银行", "weight": 0.12, "return": 0.02},
        ...
      ]
    }
"""

from typing import Dict, List, Tuple
import argparse
import csv
import json
import sys


def load_csv(filepath: str) -> List[Dict]:
    """Load sector weights and returns from CSV."""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "sector": row["sector"],
                "weight": float(row["weight"]),
                "return": float(row["return"]),
            })
    return rows


def normalize_weights(data: List[Dict]) -> List[Dict]:
    """Normalize weights to sum to 1.0."""
    total = sum(d["weight"] for d in data)
    if total <= 0:
        raise ValueError("Weights must sum to a positive number")
    if abs(total - 1.0) > 1e-6:
        print(f"[INFO] Normalizing weights from {total:.4f} to 1.0", file=sys.stderr)
        for d in data:
            d["weight"] = d["weight"] / total
    return data


def brinson_attribution(
    portfolio: List[Dict], benchmark: List[Dict]
) -> Tuple[List[Dict], Dict]:
    """
    Compute Brinson-Fachler single-period attribution.

    Args:
        portfolio: List of {"sector", "weight", "return"} for portfolio
        benchmark: List of {"sector", "weight", "return"} for benchmark

    Returns:
        (sector_results, summary)
        sector_results: per-sector attribution breakdown
        summary: aggregate results
    """
    portfolio = normalize_weights(portfolio)
    benchmark = normalize_weights(benchmark)

    # Build lookup dicts
    p_map = {d["sector"]: d for d in portfolio}
    b_map = {d["sector"]: d for d in benchmark}

    # Union of all sectors
    all_sectors = sorted(set(list(p_map.keys()) + list(b_map.keys())))

    # Benchmark total return
    rb_total = sum(d["weight"] * d["return"] for d in benchmark)

    # Portfolio total return
    rp_total = sum(d["weight"] * d["return"] for d in portfolio)

    results = []
    total_allocation = 0.0
    total_selection = 0.0
    total_interaction = 0.0

    for sector in all_sectors:
        wp = p_map[sector]["weight"] if sector in p_map else 0.0
        wb = b_map[sector]["weight"] if sector in b_map else 0.0
        rp = p_map[sector]["return"] if sector in p_map else 0.0
        rb = b_map[sector]["return"] if sector in b_map else 0.0

        # Brinson-Fachler formulas
        allocation = (wp - wb) * (rb - rb_total)
        selection = wb * (rp - rb)
        interaction = (wp - wb) * (rp - rb)
        total_effect = allocation + selection + interaction

        results.append({
            "sector": sector,
            "portfolio_weight": wp,
            "benchmark_weight": wb,
            "active_weight": wp - wb,
            "portfolio_return": rp,
            "benchmark_return": rb,
            "allocation_effect": allocation,
            "selection_effect": selection,
            "interaction_effect": interaction,
            "total_effect": total_effect,
        })

        total_allocation += allocation
        total_selection += selection
        total_interaction += interaction

    excess_return = rp_total - rb_total
    attribution_sum = total_allocation + total_selection + total_interaction

    summary = {
        "portfolio_return": rp_total,
        "benchmark_return": rb_total,
        "excess_return": excess_return,
        "total_allocation_effect": total_allocation,
        "total_selection_effect": total_selection,
        "total_interaction_effect": total_interaction,
        "attribution_sum": attribution_sum,
        "residual": excess_return - attribution_sum,  # should be ~0
    }

    return results, summary


def format_pct(value: float) -> str:
    """Format as percentage string."""
    return f"{value * 100:+.2f}%"


def print_results(results: List[Dict], summary: Dict):
    """Print attribution results as formatted table."""
    print("\n" + "=" * 100)
    print("Brinson-Fachler 单期绩效归因结果")
    print("=" * 100)

    # Header
    headers = [
        "行业", "组合权重", "基准权重", "主动权重",
        "组合收益", "基准收益", "配置效应", "选股效应", "交互效应", "合计"
    ]
    fmt = "{:<10} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}"
    print(fmt.format(*headers))
    print("-" * 100)

    # Sort by total effect descending
    sorted_results = sorted(results, key=lambda x: x["total_effect"], reverse=True)

    for r in sorted_results:
        print(fmt.format(
            r["sector"],
            f"{r['portfolio_weight']:.1%}",
            f"{r['benchmark_weight']:.1%}",
            format_pct(r["active_weight"]),
            format_pct(r["portfolio_return"]),
            format_pct(r["benchmark_return"]),
            format_pct(r["allocation_effect"]),
            format_pct(r["selection_effect"]),
            format_pct(r["interaction_effect"]),
            format_pct(r["total_effect"]),
        ))

    print("-" * 100)
    print(fmt.format(
        "合计", "", "", "",
        format_pct(summary["portfolio_return"]),
        format_pct(summary["benchmark_return"]),
        format_pct(summary["total_allocation_effect"]),
        format_pct(summary["total_selection_effect"]),
        format_pct(summary["total_interaction_effect"]),
        format_pct(summary["excess_return"]),
    ))

    print(f"\n{'─' * 50}")
    print(f"组合收益:     {format_pct(summary['portfolio_return'])}")
    print(f"基准收益:     {format_pct(summary['benchmark_return'])}")
    print(f"超额收益:     {format_pct(summary['excess_return'])}")
    print(f"  配置效应:   {format_pct(summary['total_allocation_effect'])}")
    print(f"  选股效应:   {format_pct(summary['total_selection_effect'])}")
    print(f"  交互效应:   {format_pct(summary['total_interaction_effect'])}")
    print(f"  归因合计:   {format_pct(summary['attribution_sum'])}")
    if abs(summary["residual"]) > 1e-10:
        print(f"  残差:       {format_pct(summary['residual'])}  (应为0)")
    print(f"{'─' * 50}")

    # Identify top contributors
    top_pos = max(sorted_results, key=lambda x: x["total_effect"])
    top_neg = min(sorted_results, key=lambda x: x["total_effect"])
    print(f"\n最大正贡献行业: {top_pos['sector']} ({format_pct(top_pos['total_effect'])})")
    print(f"最大负贡献行业: {top_neg['sector']} ({format_pct(top_neg['total_effect'])})")

    # Capability assessment
    if abs(summary["excess_return"]) > 1e-6:
        alloc_pct = summary["total_allocation_effect"] / summary["excess_return"] * 100
        select_pct = summary["total_selection_effect"] / summary["excess_return"] * 100
        print(f"\n配置贡献占比: {alloc_pct:.1f}%")
        print(f"选股贡献占比: {select_pct:.1f}%")
        if alloc_pct > 50:
            print("→ 配置驱动型: 超额收益主要来自行业配置能力")
        elif select_pct > 50:
            print("→ 选股驱动型: 超额收益主要来自个股选择能力")
        else:
            print("→ 均衡型: 配置和选股能力均有贡献")


def print_json(results: List[Dict], summary: Dict):
    """Print attribution results as JSON."""
    output = {
        "summary": summary,
        "sectors": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Brinson-Fachler 单期绩效归因",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--portfolio", help="组合数据CSV文件路径")
    parser.add_argument("--benchmark", help="基准数据CSV文件路径")
    parser.add_argument("--json", help="JSON格式输入数据")
    parser.add_argument("--output", choices=["table", "json"], default="table",
                        help="输出格式 (default: table)")

    args = parser.parse_args()

    if args.json:
        data = json.loads(args.json)
        portfolio = data["portfolio"]
        benchmark = data["benchmark"]
    elif args.portfolio and args.benchmark:
        portfolio = load_csv(args.portfolio)
        benchmark = load_csv(args.benchmark)
    else:
        # Demo data
        print("[INFO] No input provided, running with demo data...\n", file=sys.stderr)
        portfolio = [
            {"sector": "银行",   "weight": 0.15, "return": 0.05},
            {"sector": "医药",   "weight": 0.20, "return": 0.08},
            {"sector": "电子",   "weight": 0.18, "return": 0.12},
            {"sector": "食品饮料", "weight": 0.12, "return": 0.03},
            {"sector": "新能源",  "weight": 0.15, "return": -0.05},
            {"sector": "房地产",  "weight": 0.05, "return": -0.10},
            {"sector": "计算机",  "weight": 0.15, "return": 0.15},
        ]
        benchmark = [
            {"sector": "银行",   "weight": 0.20, "return": 0.04},
            {"sector": "医药",   "weight": 0.12, "return": 0.06},
            {"sector": "电子",   "weight": 0.15, "return": 0.10},
            {"sector": "食品饮料", "weight": 0.18, "return": 0.05},
            {"sector": "新能源",  "weight": 0.10, "return": -0.03},
            {"sector": "房地产",  "weight": 0.10, "return": -0.08},
            {"sector": "计算机",  "weight": 0.15, "return": 0.10},
        ]

    results, summary = brinson_attribution(portfolio, benchmark)

    if args.output == "json":
        print_json(results, summary)
    else:
        print_results(results, summary)


if __name__ == "__main__":
    main()
