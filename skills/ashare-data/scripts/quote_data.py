#!/usr/bin/env python3
"""Ashare 行情数据获取脚本 — 基于新浪+腾讯双核心"""
from Ashare import get_price
import argparse
import json
import os

# 将 Ashare.py 所在目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import sys


def quote(code, count=10, frequency="1d", end_date=""):
    """获取行情数据
    code: 股票代码，支持格式：sh000001 / sz000001 / 000001.XSHG / 000001.XSHE
    frequency: 1d(日线) 1w(周线) 1M(月线) 1m 5m 15m 30m 60m(分钟线)
    count: 返回K线数量
    """
    try:
        df = get_price(code, end_date=end_date, count=count, frequency=frequency)
        df = df.reset_index()
        df.columns = ["time"] + list(df.columns[1:])
        records = json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))
        return {"code": code, "frequency": frequency, "count": len(records), "data": records}
    except Exception as e:
        return {"error": str(e), "code": code}


def multi_quote(codes, count=10, frequency="1d"):
    """批量获取多只股票行情"""
    results = {}
    for code in codes:
        results[code] = quote(code, count=count, frequency=frequency)
    return results


def main():
    parser = argparse.ArgumentParser(description="Ashare 行情数据（新浪+腾讯双核心）")
    parser.add_argument("command", choices=["quote", "multi"])
    parser.add_argument("--code", "-c", required=True, help="股票代码（多个用逗号分隔），如 sh600519,sz000001")
    parser.add_argument("--count", "-n", type=int, default=30, help="K线数量（默认30）")
    parser.add_argument("--freq", "-f", default="1d", help="周期: 1d/1w/1M/1m/5m/15m/30m/60m")
    parser.add_argument("--end", "-e", default="", help="结束日期 YYYY-MM-DD")
    args = parser.parse_args()

    if args.command == "quote":
        result = quote(args.code, args.count, args.freq, args.end)
    elif args.command == "multi":
        codes = args.code.split(",")
        result = multi_quote(codes, args.count, args.freq)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
