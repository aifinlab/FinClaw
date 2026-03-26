from datetime import datetime
from typing import Any, Dict, List
import argparse
import json


def get_path(data: Dict[str, Any], path: str) -> Any:
    cur = data
    for part in path.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def safe_div(numerator: float, denominator: float) -> float:
    if denominator in (0, None):
        return None
    return numerator / denominator


def compute_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    financials = data.get("financials", {})
    monthly_income = financials.get("monthly_income")
    monthly_debt = financials.get("monthly_debt")
    operating_cashflow = financials.get("operating_cashflow")
    collateral_value = get_path(data, "collateral.collateral_value")
    loan_amount = get_path(data, "loan.amount")

    metrics = {}
    metrics["dti"] = safe_div(monthly_debt, monthly_income) if monthly_income is not None else None
    metrics["cashflow_coverage"] = safe_div(operating_cashflow, monthly_debt) if monthly_debt else None
    metrics["ltv"] = safe_div(loan_amount, collateral_value) if collateral_value else None
    return metrics


def eval_rule(value: Any, op: str, target: Any) -> bool:
    if value is None:
        return False
    if op == ">":
        return value > target
    if op == ">=":
        return value >= target
    if op == "<":
        return value < target
    if op == "<=":
        return value <= target
    if op == "==":
        return value == target
    if op == "!=":
        return value != target
    if op == "in":
        return value in target
    return False


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Retail business loan pre-check assessment")
    parser.add_argument("--input", required=True, help="Input applicant data JSON")
    parser.add_argument("--rules", required=False, help="Rules/thresholds JSON")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    data = load_json(args.input)
    rules = load_json(args.rules) if args.rules else {}

    required_fields: List[str] = rules.get("required_fields", [])
    thresholds: Dict[str, Any] = rules.get("thresholds", {})
    rule_defs: List[Dict[str, Any]] = rules.get("rules", [])

    missing_fields = []
    for field in required_fields:
        if get_path(data, field) is None:
            missing_fields.append(field)

    metrics = compute_metrics(data)
    context = {"metrics": metrics, **data}

    rule_hits = []
    for rule in rule_defs:
        field = rule.get("field")
        op = rule.get("op")
        target = rule.get("value")
        severity = rule.get("severity", "review")
        message = rule.get("message", "")
        actual = get_path(context, field)
        if eval_rule(actual, op, target):
            rule_hits.append({
                "id": rule.get("id"),
                "field": field,
                "op": op,
                "target": target,
                "actual": actual,
                "severity": severity,
                "message": message,
            })

    # basic threshold checks if provided
    threshold_hits = []
    if thresholds:
        if metrics.get("dti") is not None and thresholds.get("max_dti") is not None:
            if metrics["dti"] > thresholds["max_dti"]:
                threshold_hits.append({"id": "max_dti", "actual": metrics["dti"], "target": thresholds["max_dti"]})
        if metrics.get("cashflow_coverage") is not None and thresholds.get("min_cashflow") is not None:
            if metrics["cashflow_coverage"] < thresholds["min_cashflow"]:
                threshold_hits.append({"id": "min_cashflow", "actual": metrics["cashflow_coverage"], "target": thresholds["min_cashflow"]})
        if get_path(data, "credit_summary.inquiries_6m") is not None and thresholds.get("max_inquiries_6m") is not None:
            if get_path(data, "credit_summary.inquiries_6m") > thresholds["max_inquiries_6m"]:
                threshold_hits.append({"id": "max_inquiries_6m", "actual": get_path(data, "credit_summary.inquiries_6m"), "target": thresholds["max_inquiries_6m"]})

    all_hits = rule_hits + threshold_hits

    # decide suggestion
    severity_rank = {"block": 3, "review": 2, "warn": 1}
    max_sev = 0
    for hit in rule_hits:
        max_sev = max(max_sev, severity_rank.get(hit.get("severity", "review"), 2))
    suggestion = "pass"
    if missing_fields:
        suggestion = "hold"
    if max_sev >= 3:
        suggestion = "review"
    elif max_sev == 2 and suggestion != "hold":
        suggestion = "review"

    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "precheck_suggestion": suggestion,
        "missing_fields": missing_fields,
        "metrics": metrics,
        "rule_hits": rule_hits,
        "threshold_hits": threshold_hits,
        "next_steps": [
            "补齐缺失材料并复核关键指标",
            "对命中规则进行人工核验",
            "满足准入条件后进入尽调或面谈"
        ],
        "notes": "本结果为预审辅助意见，不构成授信审批结论。"
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
