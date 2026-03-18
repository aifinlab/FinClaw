from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd


SEVERITY_ORDER = ["critical", "high", "medium", "low"]


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def normalize_severity(value: str) -> str:
    value = (value or "").strip().lower()
    if value in SEVERITY_ORDER:
        return value
    return "medium"


def build_summary(df: pd.DataFrame) -> Dict[str, object]:
    summary = {
        "total": int(df.shape[0]),
        "by_severity": {},
        "by_type": {},
    }
    for severity, group in df.groupby("severity"):
        summary["by_severity"][severity] = int(group.shape[0])
    if "exception_type" in df.columns:
        summary["by_type"] = df["exception_type"].value_counts().to_dict()
    return summary


def build_priority(df: pd.DataFrame) -> List[Dict[str, object]]:
    priority = []
    for severity in SEVERITY_ORDER:
        subset = df[df["severity"] == severity]
        if subset.empty:
            continue
        for _, row in subset.iterrows():
            priority.append(
                {
                    "exception_id": row.get("exception_id"),
                    "exception_type": row.get("exception_type"),
                    "severity": severity,
                    "system": row.get("system"),
                    "indicator": row.get("indicator"),
                    "suggested_action": row.get("suggested_action"),
                }
            )
    return priority


def main() -> None:
    parser = argparse.ArgumentParser(description="监管报送异常定位摘要脚本")
    parser.add_argument("--input", required=True, help="异常记录 CSV/Excel")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = load_table(input_path)
    if "severity" not in df.columns:
        df["severity"] = "medium"
    df["severity"] = df["severity"].apply(normalize_severity)

    summary = build_summary(df)
    priority = build_priority(df)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "priority_list": priority,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
