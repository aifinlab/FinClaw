from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DailyAlert:
    object_id: str
    object_name: str
    priority: str
    description: str


def load_daily(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_daily_report(payload: Dict[str, object]) -> Dict[str, object]:
    alerts = payload.get("alerts", [])
    events = payload.get("events", [])
    pending = payload.get("pending_items", [])
    return {
        "date": payload.get("date", datetime.now().strftime("%Y-%m-%d")),
        "summary": payload.get("summary", ""),
        "alerts": alerts,
        "events": events,
        "pending_items": pending,
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_daily(Path(input_path))
    report = build_daily_report(payload)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build daily risk report")
    parser.add_argument("input", help="Input daily data json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
