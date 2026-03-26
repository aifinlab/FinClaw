from credit_issue_list_builder import generate_packet
from pathlib import Path
from shared.corporate_finance_task_engine import render_markdown
import argparse


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sys
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run bank-t143 corporate finance task skill.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", help="Optional output path")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    packet = generate_packet(payload)

    if args.format == "json":
        content = json.dumps(packet, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(packet)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
