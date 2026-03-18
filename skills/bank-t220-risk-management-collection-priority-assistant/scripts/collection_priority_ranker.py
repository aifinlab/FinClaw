from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


WEIGHTS = {
    "overdue_days": 0.35,
    "overdue_amount": 0.3,
    "contact_success_rate": 0.15,
    "promise_fulfillment_rate": 0.1,
    "asset_value": 0.1,
}


def _safe_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@dataclass
class RankingConfig:
    bins: List[Tuple[str, float]]


DEFAULT_BINS = [
    ("A", 0.75),
    ("B", 0.55),
    ("C", 0.35),
    ("D", 0.0),
]


def normalize_series(series: pd.Series) -> pd.Series:
    if series.max() == series.min():
        return pd.Series([0.0] * len(series), index=series.index)
    return (series - series.min()) / (series.max() - series.min())


def build_score(df: pd.DataFrame) -> pd.Series:
    normalized = {}
    for key in WEIGHTS:
        normalized[key] = normalize_series(df[key].fillna(0))
    score = sum(normalized[key] * weight for key, weight in WEIGHTS.items())
    return score.round(4)


def assign_tier(score: float, config: RankingConfig) -> str:
    for tier, threshold in config.bins:
        if score >= threshold:
            return tier
    return config.bins[-1][0]


def load_data(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("仅支持 CSV 或 Excel 文件")


def ensure_columns(df: pd.DataFrame, columns: List[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")


def build_output(df: pd.DataFrame, config: RankingConfig) -> pd.DataFrame:
    score = build_score(df)
    df = df.copy()
    df["priority_score"] = score
    df["priority_tier"] = score.apply(lambda value: assign_tier(value, config))
    df = df.sort_values(by="priority_score", ascending=False)
    return df


def summarize(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    summary = {}
    for tier, group in df.groupby("priority_tier"):
        summary[tier] = {
            "count": int(group.shape[0]),
            "avg_score": round(group["priority_score"].mean(), 4),
            "avg_overdue_days": round(group["overdue_days"].mean(), 2),
            "avg_overdue_amount": round(group["overdue_amount"].mean(), 2),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="催收优先级排序打分脚本")
    parser.add_argument("--input", required=True, help="输入 CSV/Excel 文件路径")
    parser.add_argument("--output", required=True, help="输出文件路径（csv/xlsx/json）")
    parser.add_argument(
        "--bins",
        help="分层阈值 JSON，例如: [[\"A\",0.8],[\"B\",0.6],[\"C\",0.4],[\"D\",0]]",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    df = load_data(input_path)
    required_columns = [
        "customer_id",
        "overdue_days",
        "overdue_amount",
        "contact_success_rate",
        "promise_fulfillment_rate",
        "asset_value",
    ]
    ensure_columns(df, required_columns)

    if args.bins:
        bins = json.loads(args.bins)
        config = RankingConfig(bins=[(item[0], float(item[1])) for item in bins])
    else:
        config = RankingConfig(bins=DEFAULT_BINS)

    ranked = build_output(df, config)
    summary = summarize(ranked)

    if output_path.suffix.lower() == ".json":
        payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "summary": summary,
            "records": ranked.to_dict(orient="records"),
        }
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    elif output_path.suffix.lower() == ".csv":
        ranked.to_csv(output_path, index=False)
    else:
        ranked.to_excel(output_path, index=False)


if __name__ == "__main__":
    main()
