import json
import sys
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.corporate_finance_task_engine import build_packet, render_markdown  # noqa: E402


SCENARIO_ID = "t141"


def generate_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    return build_packet(payload, SCENARIO_ID)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate t141 operating volatility monitoring brief.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", help="Optional output path")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    packet = generate_packet(payload)
    content = json.dumps(packet, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(packet)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()

