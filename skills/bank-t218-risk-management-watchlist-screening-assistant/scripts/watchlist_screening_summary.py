from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def load_payload(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(payload: Dict[str, object]) -> Dict[str, object]:
    hits = payload.get("hits", [])
    return {
        "hit_count": len(hits),
        "hits": hits,
        "priority_summary": payload.get("priority_summary", ""),
        "pending_items": payload.get("pending_items", ["核对名单更新时间与匹配规则"]),
        "recommended_actions": payload.get("recommended_actions", ["对高风险命中升级复核"]),
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_payload(Path(input_path))
    report = build_summary(payload)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build watchlist screening summary")
    parser.add_argument("input", help="Input watchlist screening json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
