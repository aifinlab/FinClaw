#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总风格暴露变化，输入为 JSON 列表。"""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

STYLE_KEYS = [
    "large_cap", "mid_cap", "small_cap",
    "growth", "value", "balanced",
    "tech", "consumer", "cyclical", "financial", "healthcare", "manufacturing",
    "quality", "momentum", "low_vol", "dividend",
    "equity_position", "turnover", "top10_concentration",
]


def load_records(path: str) -> List[Dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    series = defaultdict(list)
    for row in records:
        period = row.get("period", "未命名期间")
        for key in STYLE_KEYS:
            if key in row and row[key] is not None:
                series[key].append({"period": period, "value": row[key]})

    result: Dict[str, Any] = {"periods": [r.get("period", "") for r in records], "style_series": {}}
    for key, items in series.items():
        first = items[0]["value"]
        last = items[-1]["value"]
        result["style_series"][key] = {
            "first": first,
            "last": last,
            "change": round(last - first, 4) if isinstance(first, (int, float)) and isinstance(last, (int, float)) else None,
            "points": items,
        }
    return result


def main() -> None:
    if len(sys.argv) < 2:
        print("用法：python style_exposure_summary.py 输入.json", file=sys.stderr)
        sys.exit(1)
    records = load_records(sys.argv[1])
    summary = summarize(records)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
