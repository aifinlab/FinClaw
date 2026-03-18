import argparse
import json
from datetime import datetime
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_balance_drop_pct(balances: List[Dict[str, Any]]) -> float:
    if len(balances) < 2:
        return None
    balances_sorted = sorted(balances, key=lambda x: x.get("date"))
    start = balances_sorted[0].get("balance")
    end = balances_sorted[-1].get("balance")
    if start in (0, None):
        return None
    return (start - end) / start


def main() -> None:
    parser = argparse.ArgumentParser(description="Deposit churn warning")
    parser.add_argument("--input", required=True, help="Deposit data JSON")
    parser.add_argument("--rules", required=False, help="Thresholds JSON")
    parser.add_argument("--output", required=True, help="Output JSON")
    args = parser.parse_args()

    data = load_json(args.input)
    rules = load_json(args.rules) if args.rules else {}

    balances = data.get("balances", [])
    flows = data.get("flows", {})
    thresholds = rules.get("thresholds", {})

    balance_drop_pct = calc_balance_drop_pct(balances)
    inflow_30d = flows.get("inflow_30d")
    outflow_30d = flows.get("outflow_30d")
    outflow_ratio = None
    if inflow_30d is not None and outflow_30d is not None and (inflow_30d + outflow_30d) > 0:
        outflow_ratio = outflow_30d / (inflow_30d + outflow_30d)

    risk_flags = []
    if balance_drop_pct is not None and thresholds.get("balance_drop_pct") is not None:
        if balance_drop_pct >= thresholds["balance_drop_pct"]:
            risk_flags.append("balance_drop")
    if outflow_ratio is not None and thresholds.get("outflow_ratio") is not None:
        if outflow_ratio >= thresholds["outflow_ratio"]:
            risk_flags.append("outflow_ratio_high")

    if len(risk_flags) >= 2:
        risk_level = "high"
    elif len(risk_flags) == 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "customer_id": data.get("customer_id"),
        "balance_drop_pct": balance_drop_pct,
        "outflow_ratio": outflow_ratio,
        "risk_level": risk_level,
        "risk_flags": risk_flags,
        "next_steps": [
            "优先联系客户确认资金用途",
            "核查是否存在到期转出或代发变动",
            "如风险持续升高，升级到专项挽留"
        ],
        "notes": "预警结果仅用于经营管理，不构成违规认定。"
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
