import argparse
import json
from datetime import datetime
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def days_between(date_str: str, ref: datetime) -> int:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return (ref - dt).days
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Proof validation for retail finance")
    parser.add_argument("--input", required=True, help="Documents JSON")
    parser.add_argument("--rules", required=False, help="Rules JSON")
    parser.add_argument("--output", required=True, help="Output JSON")
    args = parser.parse_args()

    data = load_json(args.input)
    rules = load_json(args.rules) if args.rules else {}

    documents: List[Dict[str, Any]] = data.get("documents", [])
    required_docs = set(rules.get("required_docs", []))
    field_matches = rules.get("field_matches", [])
    valid_days = rules.get("valid_days", {})

    missing_docs = [doc for doc in required_docs if doc not in {d.get("doc_type") for d in documents}]

    missing_fields = []
    for doc in documents:
        fields = doc.get("fields", {})
        for k, v in fields.items():
            if v is None or v == "":
                missing_fields.append({"doc_type": doc.get("doc_type"), "field": k})

    inconsistencies = []
    for rule in field_matches:
        field = rule.get("field")
        doc_types = rule.get("doc_types", [])
        values = {}
        for doc in documents:
            if doc.get("doc_type") in doc_types:
                values[doc.get("doc_type")] = doc.get("fields", {}).get(field)
        uniq = {v for v in values.values() if v is not None}
        if len(uniq) > 1:
            inconsistencies.append({"field": field, "values": values})

    red_flags = []
    now = datetime.utcnow()
    for doc in documents:
        doc_type = doc.get("doc_type")
        issue_date = doc.get("issue_date")
        if doc_type in valid_days and issue_date:
            age = days_between(issue_date, now)
            if age is not None and age > valid_days[doc_type]:
                red_flags.append({"doc_type": doc_type, "issue_date": issue_date, "flag": "expired"})
        if issue_date is None:
            red_flags.append({"doc_type": doc_type, "flag": "missing_issue_date"})

    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "missing_docs": missing_docs,
        "missing_fields": missing_fields,
        "inconsistencies": inconsistencies,
        "red_flags": red_flags,
        "next_steps": [
            "补齐缺失材料或字段",
            "对不一致字段做人工复核",
            "对红旗材料启动升级核验"
        ],
        "notes": "自动核验仅提供辅助结论，需结合人工复核。"
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
