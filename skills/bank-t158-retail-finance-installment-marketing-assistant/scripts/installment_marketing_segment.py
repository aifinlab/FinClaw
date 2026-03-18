import argparse
import csv
import json
from typing import Any, Dict, List


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


def segment_customer(c: Dict[str, Any]) -> Dict[str, Any]:
    big_purchase = to_float(c.get("largest_purchase_3m"))
    revolving_ratio = to_float(c.get("revolving_ratio"))
    installment_history = int(float(c.get("installment_history", 0) or 0))
    on_time_rate = to_float(c.get("on_time_rate_12m"))
    risk_flag = int(float(c.get("risk_flag", 0) or 0))

    score = 0
    reasons = []

    if big_purchase >= 8000:
        score += 20
        reasons.append("近3月大额消费")
    if revolving_ratio >= 0.5:
        score += 15
        reasons.append("分期需求可能性高")
    if installment_history >= 1:
        score += 15
        reasons.append("历史分期使用")
    if on_time_rate >= 0.98:
        score += 10
        reasons.append("还款表现良好")
    if risk_flag:
        score -= 30
        reasons.append("命中风险标记")

    if score >= 45:
        segment = "高潜"
        offer = "高额分期或优惠利率"
    elif score >= 25:
        segment = "中潜"
        offer = "标准分期或分期礼包"
    else:
        segment = "低潜"
        offer = "轻触达或保持观察"

    return {
        "customer_id": c.get("customer_id"),
        "segment": segment,
        "score": score,
        "reasons": reasons,
        "offer": offer,
    }


def main():
    parser = argparse.ArgumentParser(description="分期营销客群分层")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_rows(args.input)
    results = [segment_customer(r) for r in rows]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
