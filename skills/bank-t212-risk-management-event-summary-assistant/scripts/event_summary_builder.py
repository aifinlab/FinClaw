from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class EventRecord:
    timestamp: str
    source: str
    description: str


def load_events(path: Path) -> List[EventRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    events = []
    for item in payload.get("events", []):
        events.append(
            EventRecord(
                timestamp=str(item.get("timestamp", "")),
                source=str(item.get("source", "")),
                description=str(item.get("description", "")),
            )
        )
    return events


def build_summary(events: List[EventRecord]) -> Dict[str, object]:
    timeline = [
        {"timestamp": ev.timestamp, "source": ev.source, "description": ev.description}
        for ev in sorted(events, key=lambda e: e.timestamp)
    ]
    key_points = [ev.description for ev in events[:3]]
    return {
        "summary": "；".join(key_points) if key_points else "",
        "timeline": timeline,
        "pending_items": ["确认事件关键事实与影响范围", "核验信息来源与时间节点"],
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    events = load_events(Path(input_path))
    report = build_summary(events)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build risk event summary")
    parser.add_argument("input", help="Input event json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
