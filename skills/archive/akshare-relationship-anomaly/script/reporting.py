from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

import pandas as pd


def ensure_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_outputs(
    output_dir: str | Path,
    summary: Dict[str, Any],
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
) -> None:
    out = ensure_output_dir(output_dir)
    pd.DataFrame([summary]).to_csv(out / "risk_summary.csv", index=False, encoding="utf-8-sig")
    nodes_df.to_csv(out / "graph_nodes.csv", index=False, encoding="utf-8-sig")
    edges_df.to_csv(out / "graph_edges.csv", index=False, encoding="utf-8-sig")
    with open(out / "risk_report.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
