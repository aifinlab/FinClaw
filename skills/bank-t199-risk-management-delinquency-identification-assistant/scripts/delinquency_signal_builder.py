import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


REQUIRED_FIELDS = {
    "customer_id",
    "account_id",
    "product_type",
    "statement_date",
    "due_amount",
    "paid_amount",
    "days_past_due",
    "rule_hits",
    "balance",
    "historical_avg_dpd",
}


@dataclass
class RowResult:
    risk_level: str
    risk_score: int
    signal_summary: str
    next_action: str
    missing_fields: str


RISK_ACTIONS = {
    "High": "优先排查，触发升级并安排专项催收",
    "Medium": "纳入重点跟踪，补充核验与客户回访",
    "Low": "持续监测，按常规频率复核",
}


def parse_float(value: str) -> Optional[float]:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: str) -> Optional[int]:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def collect_missing_fields(row: Dict[str, str]) -> List[str]:
    missing = []
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or str(value).strip() == "":
            missing.append(field)
    return missing


def compute_risk_score(days_past_due: Optional[int],
                       rule_hits: Optional[int],
                       due_amount: Optional[float],
                       paid_amount: Optional[float],
                       historical_avg_dpd: Optional[float]) -> int:
    score = 0
    if days_past_due is not None:
        score += min(days_past_due * 2, 40)
    if rule_hits is not None:
        score += min(rule_hits * 8, 32)
    if due_amount is not None and paid_amount is not None:
        paid_ratio = safe_divide(paid_amount, due_amount)
        if paid_ratio is not None:
            if paid_ratio < 0.5:
                score += 18
            elif paid_ratio < 0.8:
                score += 10
            elif paid_ratio < 1:
                score += 4
    if historical_avg_dpd is not None and days_past_due is not None:
        if days_past_due >= historical_avg_dpd * 1.5:
            score += 10
    return min(score, 100)


def determine_risk_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def build_summary(days_past_due: Optional[int],
                  rule_hits: Optional[int],
                  paid_ratio: Optional[float],
                  historical_avg_dpd: Optional[float]) -> str:
    parts = []
    if days_past_due is not None:
        parts.append(f"逾期天数{days_past_due}天")
    if rule_hits is not None:
        parts.append(f"命中规则{rule_hits}项")
    if paid_ratio is not None:
        parts.append(f"实还比例{paid_ratio:.0%}")
    if historical_avg_dpd is not None and days_past_due is not None:
        if days_past_due >= historical_avg_dpd * 1.5:
            parts.append("高于历史基线")
    return "，".join(parts) if parts else "缺少关键指标，无法形成完整摘要"


def process_row(row: Dict[str, str]) -> RowResult:
    missing = collect_missing_fields(row)

    days_past_due = parse_int(row.get("days_past_due", ""))
    rule_hits = parse_int(row.get("rule_hits", ""))
    due_amount = parse_float(row.get("due_amount", ""))
    paid_amount = parse_float(row.get("paid_amount", ""))
    historical_avg_dpd = parse_float(row.get("historical_avg_dpd", ""))

    paid_ratio = safe_divide(paid_amount, due_amount)

    risk_score = compute_risk_score(
        days_past_due,
        rule_hits,
        due_amount,
        paid_amount,
        historical_avg_dpd,
    )
    risk_level = determine_risk_level(risk_score)
    signal_summary = build_summary(days_past_due, rule_hits, paid_ratio, historical_avg_dpd)
    next_action = RISK_ACTIONS[risk_level]

    return RowResult(
        risk_level=risk_level,
        risk_score=risk_score,
        signal_summary=signal_summary,
        next_action=next_action,
        missing_fields=",".join(missing),
    )


def load_rows(input_path: str) -> List[Dict[str, str]]:
    with open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def write_output(output_path: str, rows: List[Dict[str, str]], results: List[RowResult]) -> None:
    if not rows:
        raise ValueError("输入为空，无法输出结果")

    fieldnames = list(rows[0].keys()) + [
        "risk_level",
        "risk_score",
        "signal_summary",
        "next_action",
        "missing_fields",
        "generated_at",
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row, result in zip(rows, results):
            output_row = dict(row)
            output_row.update(
                {
                    "risk_level": result.risk_level,
                    "risk_score": result.risk_score,
                    "signal_summary": result.signal_summary,
                    "next_action": result.next_action,
                    "missing_fields": result.missing_fields,
                    "generated_at": now,
                }
            )
            writer.writerow(output_row)


def main() -> None:
    parser = argparse.ArgumentParser(description="逾期苗头识别与分层脚本")
    parser.add_argument("--input", required=True, help="输入CSV路径")
    parser.add_argument("--output", required=True, help="输出CSV路径")
    args = parser.parse_args()

    rows = load_rows(args.input)
    results = [process_row(row) for row in rows]
    write_output(args.output, rows, results)


if __name__ == "__main__":
    main()
