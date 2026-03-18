import argparse
import csv
import json
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AccountRecord:
    account_id: str
    customer_id: str
    amount: float
    txn_time: str
    channel: str
    counterparty: str
    balance: float


DEFAULT_THRESHOLDS = {
    "large_amount": 300000.0,
    "frequency_threshold": 15,
    "low_balance": 1000.0,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_records(path: str) -> List[AccountRecord]:
    records: List[AccountRecord] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                AccountRecord(
                    account_id=row.get("account_id", "").strip(),
                    customer_id=row.get("customer_id", "").strip(),
                    amount=parse_float(row.get("amount")),
                    txn_time=row.get("txn_time", "").strip(),
                    channel=row.get("channel", "").strip(),
                    counterparty=row.get("counterparty", "").strip(),
                    balance=parse_float(row.get("balance")),
                )
            )
    return records


def group_by_account(records: List[AccountRecord]) -> Dict[str, List[AccountRecord]]:
    grouped: Dict[str, List[AccountRecord]] = {}
    for record in records:
        grouped.setdefault(record.account_id, []).append(record)
    return grouped


def evaluate_account(records: List[AccountRecord], thresholds: Dict[str, float]) -> Dict[str, object]:
    signals: List[str] = []
    score = 0
    total_amount = sum(r.amount for r in records)

    if any(r.amount >= thresholds["large_amount"] for r in records):
        score += 2
        signals.append("出现大额交易")

    if len(records) >= thresholds["frequency_threshold"]:
        score += 2
        signals.append("交易频率偏高")

    if any(r.balance <= thresholds["low_balance"] for r in records):
        score += 1
        signals.append("账户余额偏低")

    counterparties = [r.counterparty for r in records if r.counterparty]
    if counterparties:
        top_counterparty = max(set(counterparties), key=counterparties.count)
        ratio = counterparties.count(top_counterparty) / len(counterparties)
        if ratio >= 0.6:
            score += 1
            signals.append("交易对手集中度偏高")
    else:
        ratio = 0.0

    if score >= 5:
        severity = "高"
    elif score >= 3:
        severity = "中"
    else:
        severity = "低"

    return {
        "account_id": records[0].account_id,
        "customer_id": records[0].customer_id,
        "score": score,
        "severity": severity,
        "signals": signals,
        "transaction_count": len(records),
        "total_amount": round(total_amount, 2),
        "top_counterparty_ratio": round(ratio, 2),
    }


def build_report(records: List[AccountRecord], thresholds: Dict[str, float]) -> Dict[str, object]:
    grouped = group_by_account(records)
    signals = [evaluate_account(items, thresholds) for items in grouped.values()]
    summary = {"高": 0, "中": 0, "低": 0}
    for signal in signals:
        summary[signal["severity"]] += 1

    return {"summary": summary, "signals": signals}


def parse_thresholds(path: str) -> Dict[str, float]:
    if not path:
        return DEFAULT_THRESHOLDS
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    thresholds = DEFAULT_THRESHOLDS.copy()
    thresholds.update({k: v for k, v in data.items() if k in thresholds})
    return thresholds


def main() -> None:
    parser = argparse.ArgumentParser(description="高风险账户监测")
    parser.add_argument("--input", required=True, help="账户交易CSV数据")
    parser.add_argument("--thresholds", help="阈值JSON配置")
    parser.add_argument("--output", required=True, help="输出JSON")
    args = parser.parse_args()

    records = load_records(args.input)
    thresholds = parse_thresholds(args.thresholds)
    report = build_report(records, thresholds)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
