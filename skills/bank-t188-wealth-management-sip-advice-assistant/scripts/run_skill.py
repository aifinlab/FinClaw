import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sip_plan_engine import build_packet, load_input, render_markdown  # noqa: E402


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run t188 wealth management SIP advice skill.")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", help="Optional output path")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args()

    packet = build_packet(load_input(Path(args.input)))
    content = json.dumps(packet, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(packet)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
