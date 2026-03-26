from typing import Any, Dict
import argparse
import json


def to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def precheck(app: Dict[str, Any]) -> Dict[str, Any]:
    missing = []
    blockers = []
    needs_verify = []

    age = int(float(app.get("age", 0) or 0))
    credit_score = to_float(app.get("credit_score"))
    dti = to_float(app.get("debt_to_income"))
    income = to_float(app.get("monthly_income"))
    loan_amount = to_float(app.get("loan_amount"))
    income_verified = app.get("income_verified")

    required = ["age", "credit_score", "debt_to_income", "monthly_income", "loan_amount"]
    for key in required:
        if app.get(key) in (None, ""):
            missing.append(key)

    if age and (age < 18 or age > 60):
        blockers.append("年龄超出范围")
    if credit_score and credit_score < 600:
        blockers.append("征信评分偏低")
    if dti and dti > 0.55:
        blockers.append("负债收入比偏高")
    if income and loan_amount and loan_amount > income * 12:
        needs_verify.append("借款金额与收入不匹配")

    if income_verified is False:
        needs_verify.append("收入证明未核实")
    if income_verified is None:
        missing.append("income_verified")

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
    parser = argparse.ArgumentParser(description="消费贷预审初筛")
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
