from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def load_payload(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_explanation(payload: Dict[str, object]) -> Dict[str, object]:
    return {
        "subject": payload.get("subject", ""),
        "summary": payload.get("summary", ""),
        "drivers": payload.get("drivers", []),
        "evidence": payload.get("evidence", []),
        "impacts": payload.get("impacts", []),
        "pending_items": payload.get("pending_items", ["补充数据口径与样本说明"]),
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_payload(Path(input_path))
    report = build_explanation(payload)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build risk explanation report")
    parser.add_argument("input", help="Input explanation json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
