from __future__ import annotations
import json

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import argparse


def load_weekly(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_weekly_report(payload: Dict[str, object]) -> Dict[str, object]:
    return {
        "week": payload.get("week", datetime.now().strftime("%Y-%W")),
        "summary": payload.get("summary", ""),
        "trend": payload.get("trend", []),
        "key_objects": payload.get("key_objects", []),
        "events": payload.get("events", []),
        "pending_items": payload.get("pending_items", []),
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_weekly(Path(input_path))
    report = build_weekly_report(payload)
    if output_path:
        Path(output_path).write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2),
            encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description="Build weekly risk report")
   parser.add_argument("input", help="Input weekly data json file")
   parser.add_argument("--output", help="Output report path")
   args = parser.parse_args()

   main(args.input, args.output)
