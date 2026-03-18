import argparse
import csv
import json
from datetime import datetime
from typing import Any, Dict, List

DATE_FMT = "%Y-%m-%d"


def _parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FMT)
    except ValueError:
        return None


def _days_between(date_str: str, ref: datetime) -> int:
    d = _parse_date(date_str)
    if not d:
        return -1
    return (ref - d).days


def load_customers(path: str) -> List[Dict[str, Any]]:
    if path.lower().endswith(".csv"):
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict) and "customers" in data:
            return data["customers"]
        if isinstance(data, list):
            return data
        return []


def score_customer(c: Dict[str, Any], ref: datetime) -> Dict[str, Any]:
    age = int(c.get("age", 0) or 0)
    is_senior = age >= 60
    last_contact_days = _days_between(c.get("last_contact_date", ""), ref)
    complaint_90d = int(c.get("complaint_count_90d", 0) or 0)
    fraud_alert_180d = int(c.get("fraud_alert_180d", 0) or 0)
    balance_drop_30d = float(c.get("balance_drop_30d", 0) or 0)
    digital_usage_score = float(c.get("digital_usage_score", 0) or 0)
    branch_visit_30d = int(c.get("branch_visit_30d", 0) or 0)
    high_cash_withdrawal = int(c.get("high_cash_withdrawal_flag", 0) or 0)

    score = 0
    reasons = []

    if is_senior:
        score += 5
    if last_contact_days >= 60:
        score += 15
        reasons.append("60天未触达")
    if complaint_90d >= 2:
        score += 20
        reasons.append("90天投诉>=2")
    if fraud_alert_180d >= 1:
        score += 25
        reasons.append("近180天风险预警")
    if balance_drop_30d >= 20000:
        score += 10
        reasons.append("30天资产下降")
    if digital_usage_score <= 30 and branch_visit_30d >= 2:
        score += 8
        reasons.append("线下依赖明显")
    if high_cash_withdrawal:
        score += 12
        reasons.append("大额现金支取")

    if score >= 50:
        priority = "高"
    elif score >= 30:
        priority = "中"
    else:
        priority = "低"

    actions = []
    if complaint_90d >= 2:
        actions.append("优先进行服务补偿与情绪安抚")
    if fraud_alert_180d >= 1 or high_cash_withdrawal:
        actions.append("安排安全教育与反诈提醒")
    if last_contact_days >= 60:
        actions.append("安排关怀回访并核对服务需求")
    if digital_usage_score <= 30:
        actions.append("优先使用线下或电话渠道")

    return {
        "customer_id": c.get("customer_id"),
        "is_senior": is_senior,
        "priority": priority,
        "risk_score": score,
        "reasons": reasons,
        "actions": actions,
    }


def main():
    parser = argparse.ArgumentParser(description="老年客群服务风险扫描")
    parser.add_argument("--input", required=True, help="JSON/CSV 输入")
    parser.add_argument("--output", required=True, help="输出 JSON")
    parser.add_argument("--as_of", default="", help="参考日期 YYYY-MM-DD")
    args = parser.parse_args()

    ref = _parse_date(args.as_of) or datetime.today()
    customers = load_customers(args.input)

    results = [score_customer(c, ref) for c in customers]
    summary = {
        "as_of": ref.strftime(DATE_FMT),
        "total": len(results),
        "priority_count": {
            "高": sum(1 for r in results if r["priority"] == "高"),
            "中": sum(1 for r in results if r["priority"] == "中"),
            "低": sum(1 for r in results if r["priority"] == "低"),
        },
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
