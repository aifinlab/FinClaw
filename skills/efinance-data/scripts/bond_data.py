#!/usr/bin/env python3
"""
efinance 债券（可转债）数据获取脚本
支持：可转债实时行情、历史K线、基本信息、资金流向
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
    """获取可转债实时行情。非交易时段可能返回空数据"""
    try:
        df = ef.bond.get_realtime_quotes()
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"可转债行情获取失败（可能处于非交易时段）: {str(e)}"}
    if df is None or df.empty:
        return {"count": 0, "data": [], "warning": "当前无可转债行情数据"}
    return {"count": len(df), "data": _df_to_json(df)}


def quote_history(bond_code):
    """获取可转债历史K线"""
    df = ef.bond.get_quote_history(bond_code)
    return {"bond_code": bond_code, "count": len(df), "data": _df_to_json(df)}


def all_base_info():
    """获取全部可转债基本信息"""
    df = ef.bond.get_all_base_info()
    return {"count": len(df), "data": _df_to_json(df)}


def base_info(bond_code):
    """获取单只可转债基本信息"""
    info = ef.bond.get_base_info(bond_code)
    if isinstance(info, pd.Series):
        return info.to_dict()
    elif isinstance(info, pd.DataFrame) and not info.empty:
        return _df_to_json(info)
    return {"error": "未获取到数据"}


def history_bill(bond_code, days=30):
    """获取可转债资金流向"""
    df = ef.bond.get_history_bill(bond_code)
    if days and len(df) > days:
        df = df.tail(days)
    return {"bond_code": bond_code, "count": len(df), "data": _df_to_json(df)}


def main():
    parser = argparse.ArgumentParser(description="efinance 债券数据获取")
    parser.add_argument("command", choices=["realtime", "history", "all_info",
                                             "info", "bill"])
    parser.add_argument("--code", "-c", help="可转债代码")
    parser.add_argument("--days", "-d", type=int, default=30, help="资金流天数")
    args = parser.parse_args()

    try:
        if args.command == "realtime":
            result = realtime_quotes()
        elif args.command == "history":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = quote_history(args.code)
        elif args.command == "all_info":
            result = all_base_info()
        elif args.command == "info":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = base_info(args.code)
        elif args.command == "bill":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = history_bill(args.code, args.days)
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
