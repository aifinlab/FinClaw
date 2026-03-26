from dataclasses import dataclass
from typing import Dict, List
import argparse
import csv
import json


@dataclass
class TransactionRecord:
    account_id: str
    customer_id: str
    amount: float
    txn_time: str
    channel: str
    counterparty: str
    location: str
    txn_type: str


DEFAULT_THRESHOLDS = {
    "large_amount": 500000.0,
    "frequency_threshold": 10,
    "night_hours": [0, 5],
    "counterparty_ratio": 0.6,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_records(path: str) -> List[TransactionRecord]:
    records: List[TransactionRecord] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                TransactionRecord(
                    account_id=row.get("account_id", "").strip(),
                    customer_id=row.get("customer_id", "").strip(),
                    amount=parse_float(row.get("amount")),
                    txn_time=row.get("txn_time", "").strip(),
                    channel=row.get("channel", "").strip(),
                    counterparty=row.get("counterparty", "").strip(),
                    location=row.get("location", "").strip(),
                    txn_type=row.get("txn_type", "").strip(),
                )
            )
    return records


def group_by_account(records: List[TransactionRecord]) -> Dict[str, List[TransactionRecord]]:
    grouped: Dict[str, List[TransactionRecord]] = {}
    for record in records:
        grouped.setdefault(record.account_id, []).append(record)
    return grouped


def parse_hour(txn_time: str) -> int:
    try:
        return int(txn_time.split(" ")[1].split(":")[0])
    except (IndexError, ValueError):
        return -1


def evaluate_account(records: List[TransactionRecord], thresholds: Dict[str, float]) -> Dict[str, object]:
    signals: List[str] = []
    score = 0

    total_amount = sum(r.amount for r in records)
    large_txn = any(r.amount >= thresholds["large_amount"] for r in records)

    if large_txn:
        score += 2
        signals.append("出现大额交易")

    if len(records) >= thresholds["frequency_threshold"]:
        score += 2
        signals.append("交易频率偏高")

    night_start, night_end = thresholds["night_hours"]
    night_txn = [r for r in records if night_start <= parse_hour(r.txn_time) <= night_end]
    if night_txn:
        score += 1
        signals.append("夜间交易异常")

    counterparties = [r.counterparty for r in records if r.counterparty]
    if counterparties:
        top_counterparty = max(set(counterparties), key=counterparties.count)
        ratio = counterparties.count(top_counterparty) / len(counterparties)
        if ratio >= thresholds["counterparty_ratio"]:
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


def build_report(records: List[TransactionRecord], thresholds: Dict[str, float]) -> Dict[str, object]:
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
    parser = argparse.ArgumentParser(description="交易异常监测")
    parser.add_argument("--input", required=True, help="交易CSV数据")
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
