import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from statistics import median
from typing import Dict, List, Tuple


@dataclass
class CollateralRecord:
    collateral_id: str
    collateral_type: str
    valuation_date: str
    valuation_amount: float
    discount_rate: float
    coverage_ratio: float
    region: str
    last_valuation_date: str
    disposal_months: float
    exposure_balance: float


@dataclass
class CollateralSignal:
    collateral_id: str
    score: int
    signals: List[str]
    valuation_drop_pct: float
    coverage_gap_pct: float
    severity: str


DEFAULT_THRESHOLDS = {
    "valuation_drop_pct": 0.15,
    "coverage_ratio_min": 1.2,
    "discount_rate_jump": 0.08,
    "disposal_months_max": 12,
}


def parse_float(value: str) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def load_records(path: str) -> List[CollateralRecord]:
    records: List[CollateralRecord] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                CollateralRecord(
                    collateral_id=row.get("collateral_id", "").strip(),
                    collateral_type=row.get("collateral_type", "").strip(),
                    valuation_date=row.get("valuation_date", "").strip(),
                    valuation_amount=parse_float(row.get("valuation_amount")),
                    discount_rate=parse_float(row.get("discount_rate")),
                    coverage_ratio=parse_float(row.get("coverage_ratio")),
                    region=row.get("region", "").strip(),
                    last_valuation_date=row.get("last_valuation_date", "").strip(),
                    disposal_months=parse_float(row.get("disposal_months")),
                    exposure_balance=parse_float(row.get("exposure_balance")),
                )
            )
    return records


def compute_drop_pct(current_value: float, previous_value: float) -> float:
    if previous_value <= 0:
        return 0.0
    return (previous_value - current_value) / previous_value


def compute_coverage_gap_ratio(coverage_ratio: float, min_ratio: float) -> float:
    if min_ratio <= 0:
        return 0.0
    if coverage_ratio >= min_ratio:
        return 0.0
    return (min_ratio - coverage_ratio) / min_ratio


def evaluate_collateral(record: CollateralRecord, thresholds: Dict[str, float]) -> CollateralSignal:
    signals: List[str] = []
    score = 0

    valuation_drop_pct = compute_drop_pct(record.valuation_amount, record.exposure_balance)
    if valuation_drop_pct >= thresholds["valuation_drop_pct"]:
        score += 2
        signals.append("估值较授信余额显著下降")

    coverage_gap_pct = compute_coverage_gap_ratio(record.coverage_ratio, thresholds["coverage_ratio_min"])
    if coverage_gap_pct > 0:
        score += 2
        signals.append("覆盖度低于阈值")

    if record.discount_rate >= thresholds["discount_rate_jump"]:
        score += 1
        signals.append("折扣率上调幅度较大")

    if record.disposal_months >= thresholds["disposal_months_max"]:
        score += 1
        signals.append("预计处置周期偏长")

    if record.last_valuation_date:
        try:
            last_date = datetime.strptime(record.last_valuation_date, "%Y-%m-%d")
            days_since = (datetime.today() - last_date).days
            if days_since >= 180:
                score += 1
                signals.append("重估间隔过长")
        except ValueError:
            signals.append("重估日期格式异常")

    if score >= 5:
        severity = "高"
    elif score >= 3:
        severity = "中"
    else:
        severity = "低"

    return CollateralSignal(
        collateral_id=record.collateral_id,
        score=score,
        signals=signals,
        valuation_drop_pct=valuation_drop_pct,
        coverage_gap_pct=coverage_gap_pct,
        severity=severity,
    )


def summarize(signals: List[CollateralSignal]) -> Dict[str, int]:
    summary = {"高": 0, "中": 0, "低": 0}
    for signal in signals:
        summary[signal.severity] += 1
    return summary


def build_report(records: List[CollateralRecord], thresholds: Dict[str, float]) -> Dict[str, object]:
    signals = [evaluate_collateral(record, thresholds) for record in records]
    high_priority = [signal for signal in signals if signal.severity == "高"]
    summary = summarize(signals)
    median_coverage = median([r.coverage_ratio for r in records]) if records else 0.0

    return {
        "summary": summary,
        "median_coverage_ratio": round(median_coverage, 4),
        "high_priority": [signal.__dict__ for signal in high_priority],
        "all_signals": [signal.__dict__ for signal in signals],
    }


def parse_thresholds(path: str) -> Dict[str, float]:
    if not path:
        return DEFAULT_THRESHOLDS
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    thresholds = DEFAULT_THRESHOLDS.copy()
    thresholds.update({k: float(v) for k, v in data.items() if k in thresholds})
    return thresholds


def main() -> None:
    parser = argparse.ArgumentParser(description="押品监测异常识别")
    parser.add_argument("--input", required=True, help="押品监测CSV数据")
    parser.add_argument("--thresholds", help="阈值JSON配置")
    parser.add_argument("--output", required=True, help="输出JSON文件")
    args = parser.parse_args()

    records = load_records(args.input)
    thresholds = parse_thresholds(args.thresholds)
    report = build_report(records, thresholds)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
