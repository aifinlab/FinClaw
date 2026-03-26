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


def build_summary(df: pd.DataFrame) -> Dict[str, object]:
    summary = {
        "total_events": int(df.shape[0]),
        "by_status": df["status"].value_counts().to_dict() if "status" in df.columns else {},
        "by_owner": df["owner"].value_counts().to_dict() if "owner" in df.columns else {},
    }
    return summary


def build_key_items(df: pd.DataFrame) -> List[Dict[str, object]]:
    key_items = []
    for _, row in df.iterrows():
        key_items.append(
            {
                "event_id": row.get("event_id"),
                "title": row.get("title"),
                "status": row.get("status"),
                "owner": row.get("owner"),
                "deadline": row.get("deadline"),
                "risk_level": row.get("risk_level"),
                "next_action": row.get("next_action"),
            }
        )
    return key_items


def main() -> None:
    parser = argparse.ArgumentParser(description="监管报送摘要生成脚本")
    parser.add_argument("--input", required=True, help="事件清单 CSV/Excel")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = load_table(input_path)
    summary = build_summary(df)
    key_items = build_key_items(df)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "items": key_items,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
