#!/usr/bin/env python3
"""
efinance 期货数据获取脚本
支持：期货实时行情、历史K线、基本信息
"""
import sys
import json
import argparse

import efinance as ef
import pandas as pd


def _df_to_json(df, max_rows=None):
    if df is None or df.empty:
        return []
    if max_rows:
        df = df.head(max_rows)
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def realtime_quotes():
    """获取期货实时行情。非交易时段可能返回空数据"""
    try:
        df = ef.futures.get_realtime_quotes()
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"期货行情获取失败（可能处于非交易时段）: {str(e)}"}
    if df is None or df.empty:
        return {"count": 0, "data": [], "warning": "当前无期货行情数据"}
    return {"count": len(df), "data": _df_to_json(df)}


def quote_history(futures_code):
    """获取期货历史K线"""
    df = ef.futures.get_quote_history(futures_code)
    return {"futures_code": futures_code, "count": len(df), "data": _df_to_json(df)}


def futures_base_info():
    """获取期货品种基本信息"""
    df = ef.futures.get_futures_base_info()
    return {"count": len(df), "data": _df_to_json(df)}


def main():
    parser = argparse.ArgumentParser(description="efinance 期货数据获取")
    parser.add_argument("command", choices=["realtime", "history", "info"])
    parser.add_argument("--code", "-c", help="期货代码")
    args = parser.parse_args()

    try:
        if args.command == "realtime":
            result = realtime_quotes()
        elif args.command == "history":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = quote_history(args.code)
        elif args.command == "info":
            result = futures_base_info()
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
