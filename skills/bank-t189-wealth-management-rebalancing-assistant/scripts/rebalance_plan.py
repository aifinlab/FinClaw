#!/usr/bin/env python3
"""
Rebalancing plan generator for wealth management.

Input (JSON):
{
"as_of": "2026-03-15",
"base_ccy": "CNY",
"portfolio": {
    "cash": 20000.0,
    "holdings": [
    {"asset": "债券基金A", "value": 150000.0},
    {"asset": "权益基金B", "value": 120000.0},
    {"asset": "黄金ETF", "value": 30000.0}
    ]
},
"targets": [
    {"asset": "债券基金A", "target_weight": 0.45},
    {"asset": "权益基金B", "target_weight": 0.40},
    {"asset": "黄金ETF", "target_weight": 0.10},
    {"asset": "现金", "target_weight": 0.05}
],
"constraints": {
    "tolerance": 0.02,
    "min_trade_value": 2000.0,
    "max_trade_value": null,
    "allow_cash": true
}
}

Output (CSV):
asset,action,trade_value,reason

Notes:
- This is a calculation aid, not an approval decision.
- It does not account for fees, taxes, or liquidity gates.
"""

from typing import Dict, List, Tuple
import argparse
import csv
import json
import math


def _load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _normalize_targets(targets: List[Dict]) -> List[Dict]:
    total = sum(_safe_float(t.get("target_weight")) for t in targets)
    if total <= 0:
        return targets
    if abs(total - 1.0) < 1e-6:
        return targets
    # Normalize if weights do not sum to 1
    for t in targets:
        t["target_weight"] = _safe_float(t.get("target_weight")) / total
    return targets


def _build_current(holdings: List[Dict], cash: float) -> Dict[str, float]:
    current = {}
    for h in holdings:
        asset = str(h.get("asset")).strip()
        if not asset:
            continue
        current[asset] = current.get(asset, 0.0) + _safe_float(h.get("value"))
    if cash is not None:
        current["现金"] = current.get("现金", 0.0) + _safe_float(cash)
    return current


def _calc_trades(current: Dict[str, float], targets: List[Dict], tolerance: float,
                min_trade_value: float, max_trade_value: float) -> Tuple[List[Dict], Dict]:
    total_value = sum(current.values())
    target_map = {t["asset"]: _safe_float(t.get("target_weight")) for t in targets}
    target_map = {k: v for k, v in target_map.items() if k}

    # Ensure all current assets have a target (default 0 if missing)
    for asset in current.keys():
        target_map.setdefault(asset, 0.0)

    trades = []
    summary = {
        "total_value": total_value,
        "tolerance": tolerance,
        "drift": {},
    }

    for asset, cur_val in current.items():
        target_weight = target_map.get(asset, 0.0)
        target_val = total_value * target_weight
        drift = 0.0 if total_value == 0 else (cur_val / total_value - target_weight)
        summary["drift"][asset] = drift

        # Within tolerance band: no trade
        if abs(drift) <= tolerance:
            continue

        trade_value = target_val - cur_val
        # Apply min/max trade thresholds
        if abs(trade_value) < min_trade_value:
            continue
        if max_trade_value is not None and abs(trade_value) > max_trade_value:
            trade_value = math.copysign(max_trade_value, trade_value)

        action = "买入" if trade_value > 0 else "卖出"
        reason = f"偏离{drift:.2%}，目标权重{target_weight:.2%}"
        trades.append({
            "asset": asset,
            "action": action,
            "trade_value": round(trade_value, 2),
            "reason": reason,
        })

    return trades, summary


def _write_csv(path: str, trades: List[Dict]):
    fieldnames = ["asset", "action", "trade_value", "reason"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in trades:
            writer.writerow(row)


def _write_summary(path: str, summary: Dict):
    with open(path, "w", encoding="utf-8") as f:
        f.write("再平衡摘要\n")
        f.write(f"总资产: {summary.get('total_value', 0):,.2f}\n")
        f.write(f"容忍区间: ±{summary.get('tolerance', 0):.2%}\n")
        f.write("偏离度(当前权重-目标权重):\n")
        for asset, drift in summary.get("drift", {}).items():
            f.write(f"- {asset}: {drift:.2%}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate a rebalancing trade plan")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--summary", required=False, help="Path to summary txt")
    parser.add_argument("--tolerance", type=float, default=None, help="Override tolerance band")
    parser.add_argument("--min-trade", type=float, default=None, help="Override min trade value")
    parser.add_argument("--max-trade", type=float, default=None, help="Override max trade value")
    args = parser.parse_args()

    data = _load_json(args.input)
    portfolio = data.get("portfolio", {})
    holdings = portfolio.get("holdings", [])
    cash = portfolio.get("cash", 0.0)
    targets = _normalize_targets(data.get("targets", []))
    constraints = data.get("constraints", {})

    tolerance = args.tolerance if args.tolerance is not None else _safe_float(constraints.get("tolerance"), 0.02)
    min_trade_value = args.min_trade if args.min_trade is not None else _safe_float(constraints.get("min_trade_value"), 0.0)
    max_trade_value = args.max_trade if args.max_trade is not None else constraints.get("max_trade_value", None)
    if max_trade_value is not None:
        max_trade_value = _safe_float(max_trade_value)

    current = _build_current(holdings, cash)
    trades, summary = _calc_trades(current, targets, tolerance, min_trade_value, max_trade_value)

    _write_csv(args.output, trades)
    if args.summary:
        _write_summary(args.summary, summary)


if __name__ == "__main__":
    main()
