from __future__ import annotations

from check_consistency import run_consistency_check

from common import pretty_print
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="运行上市企业字段一致性校验演示")
    parser.add_argument("--symbol", default="600519", help="股票代码，默认 600519")
    parser.add_argument("--exchange", default="SSE", help="交易所，默认 SSE")
    args = parser.parse_args()

    result = run_consistency_check(
        symbol=args.symbol,
        exchange=args.exchange.upper(),
        announcement_keywords=["法定代表人", "注册地址", "注册资本", "工商变更登记"],
    )
    pretty_print(result)


if __name__ == "__main__":
    main()
