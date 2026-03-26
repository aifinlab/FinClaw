from pathlib import Path
from typing import Dict, List, Any
import argparse
import csv
import json

REQUIRED_FIELDS = [
    "customer_name",
    "business_license",
    "industry",
    "annual_revenue",
    "main_products",
    "repayment_source",
]

RISK_FLAGS = {
    "tax_invoice_missing": "税票缺失",
    "transaction_chain_missing": "交易闭环不完整",
    "negative_public_info": "负面舆情",
}


def load_record(path: Path) -> Dict[str, Any]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    return rows[0] if rows else {}


def check_required(record: Dict[str, Any]) -> List[str]:
    return [field for field in REQUIRED_FIELDS if not str(record.get(field, "")).strip()]


def build_result(record: Dict[str, Any]) -> Dict[str, Any]:
    missing = check_required(record)
    risk_notes = []
    for key, label in RISK_FLAGS.items():
        if str(record.get(key, "")).lower() in {"yes", "1", "true"}:
            risk_notes.append(label)
    status = "需补件" if missing else "可进入下一步"
    return {
        "status": status,
        "missing_fields": missing,
        "risk_notes": risk_notes,
    }


def render_markdown(result: Dict[str, Any]) -> str:
    lines = ["# 小微准入预审结果", "", f"- 状态: {result['status']}"]
    lines.append("\n## 缺失字段")
    if result["missing_fields"]:
        for field in result["missing_fields"]:
            lines.append(f"- {field}")
    else:
        lines.append("- 无")
    lines.append("\n## 风险提示")
    if result["risk_notes"]:
        for note in result["risk_notes"]:
            lines.append(f"- {note}")
    else:
        lines.append("- 未发现显性风险标签")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="小微客户准入预审")
    parser.add_argument("input", type=Path, help="输入CSV或JSON")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    record = load_record(args.input)
    result = build_result(record)

    if args.json_out:
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(render_markdown(result), encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
