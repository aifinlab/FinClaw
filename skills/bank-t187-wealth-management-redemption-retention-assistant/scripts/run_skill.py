from pathlib import Path
import argparse
import subprocess
import sys
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
    get_financial_report,
    get_fund_quote,
)
# ====================================


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
