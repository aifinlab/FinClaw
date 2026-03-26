from typing import Any, Dict, List
import argparse
import csv
import json


def load_rows(path: str) -> List[Dict[str, Any]]:
    if path.lower().endswith(".csv"):
        with open(path, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict) and "customers" in data:
            return data["customers"]
        if isinstance(data, list):
            return data
        return []


def to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def score_limit_increase(c: Dict[str, Any]) -> Dict[str, Any]:
    limit = to_float(c.get("credit_limit"))
    avg_spend = to_float(c.get("avg_spend_3m"))
    util = avg_spend / limit if limit > 0 else 0.0

    on_time_rate = to_float(c.get("on_time_rate_12m"))
    delinquency = int(float(c.get("delinquency_12m", 0) or 0))
    income = to_float(c.get("monthly_income"))
    debt_ratio = to_float(c.get("debt_to_income"))
    risk_flag = int(float(c.get("risk_flag", 0) or 0))

    score = 0
    reasons = []

    if util >= 0.7:
        score += 25
        reasons.append("额度使用率高")
    if on_time_rate >= 0.98:
        score += 25
        reasons.append("近12月按时还款")
    if delinquency == 0:
        score += 15
        reasons.append("无逾期记录")
    if income >= 12000:
        score += 10
        reasons.append("收入水平较高")
    if debt_ratio <= 0.4:
        score += 10
        reasons.append("负债率可控")
    if risk_flag:
        score -= 40
        reasons.append("命中风险标记")

    if score >= 60:
        decision = "建议提额"
    elif score >= 40:
        decision = "可观察"
    else:
        decision = "暂缓"

    return {
        "customer_id": c.get("customer_id"),
        "utilization": round(util, 4),
        "score": score,
        "decision": decision,
        "reasons": reasons,
    }


def main():
    parser = argparse.ArgumentParser(description="信用卡提额机会评分")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_rows(args.input)
    results = [score_limit_increase(r) for r in rows]
    results.sort(key=lambda x: x["score"], reverse=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
