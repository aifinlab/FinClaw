from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


REQUIRED_FIELDS = ["visit_date", "customer_name", "loan_balance", "purpose", "site_findings"]


def load_minutes(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_minutes(payload: Dict[str, object]) -> Dict[str, object]:
    missing_fields = [field for field in REQUIRED_FIELDS if not payload.get(field)]
    issues: List[str] = []
    if payload.get("loan_balance") is None:
        issues.append("缺少贷款余额")
    if payload.get("site_findings") is None:
        issues.append("缺少现场检查发现")
    return {
        "summary": payload.get("summary", ""),
        "missing_fields": missing_fields,
        "issues": issues,
        "pending_items": payload.get("pending_items", ["补充纪要附件或影像材料"]),
        "recommended_actions": payload.get("recommended_actions", ["安排复核并确认现场发现"]),
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_minutes(Path(input_path))
    report = check_minutes(payload)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check post-loan minutes")
    parser.add_argument("input", help="Input minutes json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
