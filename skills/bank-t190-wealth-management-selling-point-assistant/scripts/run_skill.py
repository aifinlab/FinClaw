import json
from pathlib import Path

from wealth_management_selling_points import build_packet, load_input, render_markdown


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run wealth management selling point assistant.")
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
