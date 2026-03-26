from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict
import argparse
import json

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def build_response(row: pd.Series) -> Dict[str, object]:
    return {
        "question": row.get("question"),
        "summary": row.get("summary"),
        "policy_reference": row.get("policy_reference"),
        "effective_date": row.get("effective_date"),
        "scope": row.get("scope"),
        "exceptions": row.get("exceptions"),
        "escalation": row.get("escalation"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="制度问答结构化模板生成")
    parser.add_argument("--input", required=True, help="问题与条款清单 CSV/Excel")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = load_table(input_path)
    responses = [build_response(row) for _, row in df.iterrows()]

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "responses": responses,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
