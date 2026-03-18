from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def load_payload(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(payload: Dict[str, object]) -> Dict[str, object]:
    return {
        "match_summary": payload.get("match_summary", ""),
        "evidence": payload.get("evidence", []),
        "false_positive_checks": payload.get("false_positive_checks", ["核对证件号/统一信用代码", "确认名单更新时间与版本"]),
        "pending_items": payload.get("pending_items", ["补充客户身份核验材料"]),
        "recommended_actions": payload.get("recommended_actions", ["必要时升级合规复核"]),
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_payload(Path(input_path))
    report = build_report(payload)
    if output_path:
        Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build list check report")
    parser.add_argument("input", help="Input list check json file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()

    main(args.input, args.output)
