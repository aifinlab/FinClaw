from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def build_tasks(df: pd.DataFrame) -> List[Dict[str, object]]:
    tasks = []
    for _, row in df.iterrows():
        tasks.append(
            {
                "item_id": row.get("item_id"),
                "original_text": row.get("original_text"),
                "risk_notes": row.get("risk_notes"),
                "suggested_focus": row.get("suggested_focus"),
            }
        )
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="合规改写任务清单生成")
    parser.add_argument("--input", required=True, help="改写任务 CSV/Excel")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = load_table(input_path)
    tasks = build_tasks(df)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tasks": tasks,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
