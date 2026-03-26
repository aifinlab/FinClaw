from typing import Any, Dict, List
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
    down_payment_ratio = to_float(app.get("down_payment_ratio"))
    income_verified = app.get("income_verified")
    property_type = app.get("property_type")

    required = ["age", "credit_score", "debt_to_income", "down_payment_ratio", "property_type"]
    for key in required:
        if app.get(key) in (None, ""):
            missing.append(key)

    if age and (age < 18 or age > 65):
        blockers.append("年龄超出范围")
    if credit_score and credit_score < 650:
        blockers.append("征信评分偏低")
    if dti and dti > 0.5:
        blockers.append("负债收入比偏高")
    if down_payment_ratio and down_payment_ratio < 0.3:
        blockers.append("首付比例不足")
    if property_type and property_type not in ["住宅", "公寓", "商品房"]:
        needs_verify.append("房产类型需人工确认")

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
    parser = argparse.ArgumentParser(description="房贷预审初筛")
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
