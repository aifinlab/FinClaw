from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse
import json

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def check_required(df: pd.DataFrame, required: List[str]) -> List[Dict[str, object]]:
    issues = []
    for field in required:
        if field not in df.columns:
            issues.append({"field": field, "issue": "missing_field", "detail": "字段缺失"})
            continue
        missing_count = int(df[field].isna().sum())
        if missing_count:
            issues.append(
                {"field": field, "issue": "missing_value", "detail": f"缺失 {missing_count} 条"}
            )
    return issues


def check_trace_id(df: pd.DataFrame, trace_field: str) -> List[Dict[str, object]]:
    if trace_field not in df.columns:
        return []
    duplicated = int(df.duplicated(subset=[trace_field]).sum())
    if duplicated:
        return [
            {
                "field": trace_field,
                "issue": "duplicate_trace_id",
                "detail": f"重复 {duplicated} 条",
            }
        ]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="留痕完整性检查脚本")
    parser.add_argument("--input", required=True, help="留痕清单 CSV/Excel")
    parser.add_argument("--required", required=True, help="必填字段 JSON 列表")
    parser.add_argument("--trace-field", default="trace_id", help="留痕编号字段")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    df = load_table(Path(args.input))
    required_fields = json.loads(Path(args.required).read_text(encoding="utf-8"))

    issues = []
    issues.extend(check_required(df, required_fields))
    issues.extend(check_trace_id(df, args.trace_field))

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "issue_count": len(issues),
        "issues": issues,
    }
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
