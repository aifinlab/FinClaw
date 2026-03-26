from __future__ import annotations
import json

from pathlib import Path
from typing import Dict, Optional
import argparse


def load_payload(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def risk_level(score: float) -> str:
    if score >= 80:
        return "高"
    if score >= 50:
        return "中"
    return "低"


def build_report(payload: Dict[str, object]) -> Dict[str, object]:
    score = float(payload.get("score", 0))
    level = risk_level(score)
    return {
        "score": score,
        "risk_level": level,
        "signals": payload.get("signals", []),
        "pending_items": payload.get("pending_items", ["补充设备指纹或行为轨迹"]),
        "recommended_actions": payload.get("recommended_actions", ["高风险升级复核"]),
    }


def main(input_path: str, output_path: Optional[str] = None) -> None:
    payload = load_payload(Path(input_path))
    report = build_report(payload)
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

   parser = argparse.ArgumentParser(
       description="Build anti-fraud triage report")
   parser.add_argument("input", help="Input anti-fraud json file")
   parser.add_argument("--output", help="Output report path")
   args = parser.parse_args()

   main(args.input, args.output)
