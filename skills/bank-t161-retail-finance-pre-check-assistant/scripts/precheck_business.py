import argparse
import json
from typing import Any, Dict


def to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def precheck(app: Dict[str, Any]) -> Dict[str, Any]:
    missing = []
    blockers = []
    needs_verify = []

    business_years = to_float(app.get("business_years"))
    revenue = to_float(app.get("annual_revenue"))
    cashflow_coverage = to_float(app.get("cashflow_coverage"))
    tax_compliance = app.get("tax_compliance")
    legal_dispute = int(float(app.get("legal_dispute_flag", 0) or 0))

    required = ["business_years", "annual_revenue", "cashflow_coverage", "tax_compliance"]
    for key in required:
        if app.get(key) in (None, ""):
            missing.append(key)

    if business_years and business_years < 2:
        blockers.append("经营年限不足")
    if revenue and revenue < 300000:
        needs_verify.append("收入规模偏低需复核")
    if cashflow_coverage and cashflow_coverage < 1.2:
        blockers.append("现金流覆盖不足")
    if tax_compliance is False:
        blockers.append("税务合规问题")
    if legal_dispute:
        needs_verify.append("涉诉信息需核验")

    if blockers:
        result = "阻断"
    elif missing:
        result = "待补资料"
    else:
        result = "可推进"

    return {
        "applicant_id": app.get("applicant_id"),
        "result": result,
        "blockers": blockers,
        "needs_verify": needs_verify,
        "missing_fields": missing,
    }


def main():
    parser = argparse.ArgumentParser(description="经营贷预审初筛")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    apps = data["applications"] if isinstance(data, dict) and "applications" in data else data
    results = [precheck(a) for a in apps]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
