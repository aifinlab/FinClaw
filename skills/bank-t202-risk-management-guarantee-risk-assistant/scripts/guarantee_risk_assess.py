from dataclasses import dataclass
from typing import Dict, List
import argparse
import csv
import json


@dataclass
class GuaranteeRecord:
    guarantor_id: str
    guarantor_name: str
    guarantee_balance: float
    coverage_ratio: float
    compensation_amount: float
    litigation_flag: str
    negative_flag: str
    last_review_date: str
    industry: str


DEFAULT_THRESHOLDS = {
    "coverage_ratio_min": 1.1,
    "compensation_ratio": 0.05,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_records(path: str) -> List[GuaranteeRecord]:
    records: List[GuaranteeRecord] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                GuaranteeRecord(
                    guarantor_id=row.get("guarantor_id", "").strip(),
                    guarantor_name=row.get("guarantor_name", "").strip(),
                    guarantee_balance=parse_float(row.get("guarantee_balance")),
                    coverage_ratio=parse_float(row.get("coverage_ratio")),
                    compensation_amount=parse_float(row.get("compensation_amount")),
                    litigation_flag=row.get("litigation_flag", "").strip(),
                    negative_flag=row.get("negative_flag", "").strip(),
                    last_review_date=row.get("last_review_date", "").strip(),
                    industry=row.get("industry", "").strip(),
                )
            )
    return records


def evaluate_record(record: GuaranteeRecord, thresholds: Dict[str, float]) -> Dict[str, object]:
    signals: List[str] = []
    score = 0

    if record.coverage_ratio and record.coverage_ratio < thresholds["coverage_ratio_min"]:
        score += 2
        signals.append("担保覆盖度低于阈值")

    if record.guarantee_balance > 0:
        compensation_ratio = record.compensation_amount / record.guarantee_balance
    else:
        compensation_ratio = 0.0

    if compensation_ratio >= thresholds["compensation_ratio"]:
        score += 2
        signals.append("代偿比例偏高")

    if record.litigation_flag == "Y":
        score += 2
        signals.append("涉诉风险提示")

    if record.negative_flag == "Y":
        score += 1
        signals.append("负面舆情提示")

    if score >= 5:
        severity = "高"
    elif score >= 3:
        severity = "中"
    else:
        severity = "低"

    return {
        "guarantor_id": record.guarantor_id,
        "guarantor_name": record.guarantor_name,
        "score": score,
        "severity": severity,
        "signals": signals,
        "coverage_ratio": record.coverage_ratio,
        "compensation_ratio": round(compensation_ratio, 4),
    }


def build_report(records: List[GuaranteeRecord], thresholds: Dict[str, float]) -> Dict[str, object]:
    signals = [evaluate_record(record, thresholds) for record in records]
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
    thresholds.update({k: float(v) for k, v in data.items() if k in thresholds})
    return thresholds


def main() -> None:
    parser = argparse.ArgumentParser(description="担保风险识别")
    parser.add_argument("--input", required=True, help="担保数据CSV")
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
