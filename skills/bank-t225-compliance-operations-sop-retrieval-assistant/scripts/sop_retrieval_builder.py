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


def build_steps(df: pd.DataFrame) -> List[Dict[str, object]]:
    steps = []
    for _, row in df.iterrows():
        steps.append(
            {
                "step_id": row.get("step_id"),
                "action": row.get("action"),
                "owner": row.get("owner"),
                "system": row.get("system"),
                "controls": row.get("controls"),
                "exceptions": row.get("exceptions"),
                "evidence": row.get("evidence"),
            }
        )
    return steps


def main() -> None:
    parser = argparse.ArgumentParser(description="SOP步骤清单生成")
    parser.add_argument("--input", required=True, help="SOP条款 CSV/Excel")
    parser.add_argument("--output", required=True, help="输出 JSON 文件")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = load_table(input_path)
    steps = build_steps(df)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "steps": steps,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
