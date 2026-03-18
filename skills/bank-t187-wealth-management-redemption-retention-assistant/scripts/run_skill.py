import argparse
from pathlib import Path
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Run wealth redemption retention assistant")
    parser.add_argument("input", type=str, help="Path to input JSON")
    parser.add_argument("--output", type=str, default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()

    script = Path(__file__).parent / "wealth_redemption_retention.py"
    cmd = [sys.executable, str(script), args.input, "--output", args.output]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
