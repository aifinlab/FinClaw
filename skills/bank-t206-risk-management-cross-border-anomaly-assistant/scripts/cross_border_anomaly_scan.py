from dataclasses import dataclass
from typing import Dict, List
import argparse
import csv
import json


@dataclass
class CrossBorderTxn:
    customer_id: str
    account_id: str
    amount: float
    currency: str
    txn_time: str
    counterparty_country: str
    trade_match: str
    counterparty: str


DEFAULT_THRESHOLDS = {
    "large_amount": 500000.0,
    "high_risk_country_ratio": 0.3,
    "currency_switch_ratio": 0.4,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_records(path: str) -> List[CrossBorderTxn]:
    records: List[CrossBorderTxn] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                CrossBorderTxn(
                    customer_id=row.get("customer_id", "").strip(),
                    account_id=row.get("account_id", "").strip(),
                    amount=parse_float(row.get("amount")),
                    currency=row.get("currency", "").strip(),
                    txn_time=row.get("txn_time", "").strip(),
                    counterparty_country=row.get("counterparty_country", "").strip(),
                    trade_match=row.get("trade_match", "").strip(),
                    counterparty=row.get("counterparty", "").strip(),
                )
            )
    return records


def group_by_customer(records: List[CrossBorderTxn]) -> Dict[str, List[CrossBorderTxn]]:
    grouped: Dict[str, List[CrossBorderTxn]] = {}
    for record in records:
        grouped.setdefault(record.customer_id, []).append(record)
    return grouped


def evaluate_customer(records: List[CrossBorderTxn], thresholds: Dict[str, float]) -> Dict[str, object]:
    signals: List[str] = []
    score = 0
    total_amount = sum(r.amount for r in records)

    if any(r.amount >= thresholds["large_amount"] for r in records):
        score += 2
        signals.append("出现大额跨境交易")

    high_risk_countries = [r for r in records if r.counterparty_country in {"IR", "KP", "SY"}]
    if records:
        high_risk_ratio = len(high_risk_countries) / len(records)
    else:
        high_risk_ratio = 0.0

    if high_risk_ratio >= thresholds["high_risk_country_ratio"]:
        score += 2
        signals.append("高风险国家交易占比偏高")

    currencies = [r.currency for r in records if r.currency]
    if currencies:
        distinct_currency_ratio = len(set(currencies)) / len(currencies)
    else:
        distinct_currency_ratio = 0.0

    if distinct_currency_ratio >= thresholds["currency_switch_ratio"]:
        score += 1
        signals.append("币种切换频繁")

    if any(r.trade_match == "N" for r in records):
        score += 1
        signals.append("贸易背景不匹配")

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
        "high_risk_country_ratio": round(high_risk_ratio, 2),
        "currency_distinct_ratio": round(distinct_currency_ratio, 2),
    }


def build_report(records: List[CrossBorderTxn], thresholds: Dict[str, float]) -> Dict[str, object]:
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
    parser = argparse.ArgumentParser(description="跨境异常交易识别")
    parser.add_argument("--input", required=True, help="跨境交易CSV数据")
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
