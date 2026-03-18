import argparse
import json
from datetime import datetime
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Credit bureau interpretation")
    parser.add_argument("--input", required=True, help="Bureau summary JSON")
    parser.add_argument("--rules", required=False, help="Thresholds JSON")
    parser.add_argument("--output", required=True, help="Output JSON")
    args = parser.parse_args()

    data = load_json(args.input)
    rules = load_json(args.rules) if args.rules else {}

    summary = data.get("summary", {})
    thresholds = rules.get("thresholds", {})

    missing_fields = [k for k in ["inquiries_3m", "inquiries_6m", "delinquencies_12m", "revolving_utilization"] if k not in summary]

    flags = []
    if summary.get("inquiries_3m") is not None and thresholds.get("max_inquiries_3m") is not None:
        if summary["inquiries_3m"] > thresholds["max_inquiries_3m"]:
            flags.append({"field": "inquiries_3m", "actual": summary["inquiries_3m"], "target": thresholds["max_inquiries_3m"], "note": "近3个月查询次数偏高"})
    if summary.get("revolving_utilization") is not None and thresholds.get("max_utilization") is not None:
        if summary["revolving_utilization"] > thresholds["max_utilization"]:
            flags.append({"field": "revolving_utilization", "actual": summary["revolving_utilization"], "target": thresholds["max_utilization"], "note": "循环额度使用率偏高"})
    if summary.get("delinquencies_12m") is not None and thresholds.get("max_delinquencies_12m") is not None:
        if summary["delinquencies_12m"] > thresholds["max_delinquencies_12m"]:
            flags.append({"field": "delinquencies_12m", "actual": summary["delinquencies_12m"], "target": thresholds["max_delinquencies_12m"], "note": "近12个月存在逾期"})

    interpretation = []
    if summary.get("max_dpd_24m"):
        interpretation.append(f"近24个月最高逾期天数为{summary['max_dpd_24m']}天。")
    if summary.get("total_balance"):
        interpretation.append(f"存量负债余额约{summary['total_balance']}。")

    questions = [
        "近期多头查询的原因是什么？是否为集中申请贷款？",
        "循环额度使用率高是否与经营资金周转相关？",
        "逾期是否为短期现金流波动导致？",
        "现有贷款的还款来源与稳定性如何？"
    ]

    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "report_date": data.get("report_date"),
        "flags": flags,
        "interpretation": interpretation,
        "questions": questions,
        "missing_fields": missing_fields,
        "notes": "征信解读为辅助结论，需结合面谈与补充材料核验。"
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
