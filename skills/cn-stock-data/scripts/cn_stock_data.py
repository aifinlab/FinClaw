# -*- coding: utf-8 -*-
"""cn-stock-data: Unified Chinese stock data CLI.

Usage:
  python cn_stock_data.py kline --code SH600519 --freq daily --start 2026-01-01
  python cn_stock_data.py quote --code SH600519,SZ000001
  python cn_stock_data.py fund_flow --code SZ000001
  python cn_stock_data.py finance --code SH600519
  python cn_stock_data.py north_flow
  python cn_stock_data.py status
"""
from routing import execute_with_fallback, get_available_sources
import argparse
import json
import os

# Ensure scripts/ is on path
sys.path.insert(0, os.path.dirname(__file__))

import sys


def cmd_kline(args):
    result = execute_with_fallback(
        data_type="kline",
        method_name="get_kline",
        code=args.code,
        force_source=args.source,
        freq=args.freq,
        start=args.start,
        end=args.end,
        count=args.count,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


def cmd_quote(args):
    codes = [c.strip() for c in args.code.split(",")]
    result = execute_with_fallback(
        data_type="quote",
        method_name="get_quote",
        code=codes[0],  # for routing decision
        force_source=args.source,
        codes=codes,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


def cmd_fund_flow(args):
    result = execute_with_fallback(
        data_type="fund_flow",
        method_name="get_fund_flow",
        code=args.code,
        force_source=args.source,
        days=args.days,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


def cmd_finance(args):
    result = execute_with_fallback(
        data_type="finance",
        method_name="get_finance",
        code=args.code,
        force_source=args.source,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


def cmd_north_flow(args):
    result = execute_with_fallback(
        data_type="north_flow",
        method_name="get_north_flow",
        force_source=args.source,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


def cmd_status(args):
    sources = get_available_sources()
    print(json.dumps({"sources": sources}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="cn-stock-data unified CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # kline
    p = sub.add_parser("kline", help="K-line history data")
    p.add_argument("--code", required=True, help="Stock code, e.g. SH600519")
    p.add_argument("--freq", default="daily",
                    choices=["daily", "weekly", "monthly", "1min", "5min", "15min", "30min", "60min"])
    p.add_argument("--start", default="", help="Start date YYYY-MM-DD")
    p.add_argument("--end", default="", help="End date YYYY-MM-DD")
    p.add_argument("--count", type=int, default=0, help="Max rows (0=all)")
    p.add_argument("--source", default=None, help="Force data source")
    p.set_defaults(func=cmd_kline)

    # quote
    p = sub.add_parser("quote", help="Realtime quote")
    p.add_argument("--code", required=True, help="Comma-separated codes")
    p.add_argument("--source", default=None)
    p.set_defaults(func=cmd_quote)

    # fund_flow
    p = sub.add_parser("fund_flow", help="Fund flow data")
    p.add_argument("--code", required=True)
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--source", default=None)
    p.set_defaults(func=cmd_fund_flow)

    # finance
    p = sub.add_parser("finance", help="Financial indicators")
    p.add_argument("--code", required=True)
    p.add_argument("--source", default=None)
    p.set_defaults(func=cmd_finance)

    # north_flow
    p = sub.add_parser("north_flow", help="Northbound capital flow")
    p.add_argument("--source", default=None)
    p.set_defaults(func=cmd_north_flow)

    # status
    p = sub.add_parser("status", help="Check data source availability")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
