from dataclasses import dataclass
from typing import Dict, List
import argparse
import csv
import json


@dataclass
class CorporateTxn:
    customer_id: str
    account_id: str
    amount: float
    currency: str
    txn_time: str
    counterparty: str
    counterparty_country: str
    industry_match: str
    trade_background: str


DEFAULT_THRESHOLDS = {
    "large_amount": 1000000.0,
    "cross_border_ratio": 0.4,
    "counterparty_concentration": 0.5,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_records(path: str) -> List[CorporateTxn]:
    records: List[CorporateTxn] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                CorporateTxn(
                    customer_id=row.get("customer_id", "").strip(),
                    account_id=row.get("account_id", "").strip(),
                    amount=parse_float(row.get("amount")),
                    currency=row.get("currency", "").strip(),
                    txn_time=row.get("txn_time", "").strip(),
                    counterparty=row.get("counterparty", "").strip(),
                    counterparty_country=row.get("counterparty_country", "").strip(),
                    industry_match=row.get("industry_match", "").strip(),
                    trade_background=row.get("trade_background", "").strip(),
                )
            )
    return records


def group_by_customer(records: List[CorporateTxn]) -> Dict[str, List[CorporateTxn]]:
    grouped: Dict[str, List[CorporateTxn]] = {}
    for record in records:
        grouped.setdefault(record.customer_id, []).append(record)
    return grouped


def evaluate_customer(records: List[CorporateTxn], thresholds: Dict[str, float]) -> Dict[str, object]:
    signals: List[str] = []
    score = 0
    total_amount = sum(r.amount for r in records)

    large_txn = any(r.amount >= thresholds["large_amount"] for r in records)
    if large_txn:
        score += 2
        signals.append("出现大额交易")

    cross_border = [r for r in records if r.counterparty_country and r.counterparty_country != "CN"]
    if records:
        cross_border_ratio = len(cross_border) / len(records)
    else:
        cross_border_ratio = 0.0

    if cross_border_ratio >= thresholds["cross_border_ratio"]:
        score += 2
        signals.append("跨境交易占比偏高")

    counterparties = [r.counterparty for r in records if r.counterparty]
    if counterparties:
        top_counterparty = max(set(counterparties), key=counterparties.count)
        concentration = counterparties.count(top_counterparty) / len(counterparties)
    else:
        concentration = 0.0

    if concentration >= thresholds["counterparty_concentration"]:
        score += 1
        signals.append("对手方集中度偏高")

    if any(r.industry_match == "N" for r in records):
        score += 1
        signals.append("行业匹配度偏低")

    if any(r.trade_background == "N" for r in records):
        score += 1
        signals.append("贸易背景不清晰")

    if score >= 5:
        severity = "高"
    elif score >= 3:
        severity = "中"
    else:
        severity = "低"

    return {
        "customer_id": records[0].customer_id,
        "score": score,
        "severity": severity,
        "signals": signals,
        "transaction_count": len(records),
        "total_amount": round(total_amount, 2),
        "cross_border_ratio": round(cross_border_ratio, 2),
        "counterparty_concentration": round(concentration, 2),
    }


def build_report(records: List[CorporateTxn], thresholds: Dict[str, float]) -> Dict[str, object]:
    grouped = group_by_customer(records)
    signals = [evaluate_customer(items, thresholds) for items in grouped.values()]
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
    parser = argparse.ArgumentParser(description="对公可疑交易识别")
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
