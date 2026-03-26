from datetime import datetime
from typing import Any, Dict, List
import argparse
import json


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_drop_pct(series: List[Dict[str, Any]], key: str) -> float:
    if len(series) < 2:
        return None
    series_sorted = sorted(series, key=lambda x: x.get("date"))
    start = series_sorted[0].get(key)
    end = series_sorted[-1].get(key)
    if start in (0, None):
        return None
    return (start - end) / start


def main() -> None:
    parser = argparse.ArgumentParser(description="Wealth churn warning")
    parser.add_argument("--input", required=True, help="Wealth data JSON")
    parser.add_argument("--rules", required=False, help="Thresholds JSON")
    parser.add_argument("--output", required=True, help="Output JSON")
    args = parser.parse_args()

    data = load_json(args.input)
    rules = load_json(args.rules) if args.rules else {}

    aum_series = data.get("aum", [])
    thresholds = rules.get("thresholds", {})

    aum_drop_pct = calc_drop_pct(aum_series, "value")
    redemptions_30d = data.get("redemptions_30d")
    maturity_60d = data.get("maturity_60d")

    latest_aum = None
    if aum_series:
        latest_aum = sorted(aum_series, key=lambda x: x.get("date"))[-1].get("value")

    redemption_ratio = None
    if latest_aum and redemptions_30d is not None:
        redemption_ratio = redemptions_30d / latest_aum if latest_aum else None

    maturity_ratio = None
    if latest_aum and maturity_60d is not None:
        maturity_ratio = maturity_60d / latest_aum if latest_aum else None

    risk_flags = []
    if aum_drop_pct is not None and thresholds.get("aum_drop_pct") is not None:
        if aum_drop_pct >= thresholds["aum_drop_pct"]:
            risk_flags.append("aum_drop")
    if redemption_ratio is not None and thresholds.get("redemption_ratio") is not None:
        if redemption_ratio >= thresholds["redemption_ratio"]:
            risk_flags.append("redemption_ratio_high")
    if maturity_ratio is not None and thresholds.get("maturity_ratio") is not None:
        if maturity_ratio >= thresholds["maturity_ratio"]:
            risk_flags.append("maturity_concentration")

    if len(risk_flags) >= 2:
        risk_level = "high"
    elif len(risk_flags) == 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "customer_id": data.get("customer_id"),
        "aum_drop_pct": aum_drop_pct,
        "redemption_ratio": redemption_ratio,
        "maturity_ratio": maturity_ratio,
        "risk_level": risk_level,
        "risk_flags": risk_flags,
        "next_steps": [
            "优先触达了解赎回原因",
            "提供匹配风险偏好的替代产品方案",
            "对集中到期客户安排续作计划"
        ],
        "notes": "预警结果仅用于经营管理，不构成收益承诺或违规认定。"
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
