#!/usr/bin/env python3
"""
efinance 基金数据获取脚本
支持：基金净值历史、持仓明细、行业分布、基金经理、阶段涨幅
"""
import argparse
import efinance as ef
import json

import pandas as pd
import sys


def _df_to_json(df, max_rows=None):
    if df is None or df.empty:
        return []
    if max_rows:
        df = df.head(max_rows)
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def quote_history(fund_code):
    """获取基金净值历史"""
    df = ef.fund.get_quote_history(fund_code)
    return {"fund_code": fund_code, "count": len(df), "data": _df_to_json(df)}


def quote_history_multi(fund_codes):
    """批量获取多只基金净值历史"""
    df = ef.fund.get_quote_history_multi(fund_codes)
    results = {}
    if isinstance(df, dict):
        for code, sub_df in df.items():
            results[code] = {"count": len(sub_df), "data": _df_to_json(sub_df)}
    elif isinstance(df, pd.DataFrame) and not df.empty:
        for code in fund_codes:
            sub = df[df.iloc[:, 0] == code] if len(df.columns) > 0 else pd.DataFrame()
            results[code] = {"count": len(sub), "data": _df_to_json(sub)}
    return results


def invest_position(fund_code):
    """获取基金持仓（重仓股）"""
    df = ef.fund.get_invest_position(fund_code)
    return {"fund_code": fund_code, "count": len(df), "data": _df_to_json(df)}


def industry_distribution(fund_code):
    """获取基金行业分布"""
    df = ef.fund.get_industry_distribution(fund_code)
    return {"fund_code": fund_code, "count": len(df), "data": _df_to_json(df)}


def fund_manager(fund_code):
    """获取基金经理信息"""
    df = ef.fund.get_fund_manager(fund_code)
    if isinstance(df, pd.DataFrame) and not df.empty:
        return {"fund_code": fund_code, "data": _df_to_json(df)}
    return {"fund_code": fund_code, "data": []}


def period_change(fund_code):
    """获取基金阶段涨幅（近1月/3月/6月/1年/3年等）"""
    df = ef.fund.get_period_change(fund_code)
    if isinstance(df, pd.DataFrame) and not df.empty:
        return {"fund_code": fund_code, "data": _df_to_json(df)}
    elif isinstance(df, pd.Series):
        return {"fund_code": fund_code, "data": df.to_dict()}
    return {"fund_code": fund_code, "data": []}


def fund_base_info(fund_code):
    """获取基金基本信息"""
    info = ef.fund.get_base_info(fund_code)
    if isinstance(info, pd.Series):
        return info.to_dict()
    elif isinstance(info, pd.DataFrame) and not info.empty:
        return _df_to_json(info)
    return {"error": "未获取到数据"}


def fund_codes(fund_type=None):
    """获取基金代码列表"""
    df = ef.fund.get_fund_codes()
    if fund_type and isinstance(df, pd.DataFrame) and not df.empty:
        type_col = [c for c in df.columns if "类型" in c]
        if type_col:
            df = df[df[type_col[0]].str.contains(fund_type, na=False)]
    return {"count": len(df), "data": _df_to_json(df)}


def main():
    parser = argparse.ArgumentParser(description="efinance 基金数据获取")
    parser.add_argument("command", choices=["history", "history_multi", "position",
                                             "industry", "manager", "period",
                                             "info", "codes"])
    parser.add_argument("--code", "-c", help="基金代码，多个用逗号分隔")
    parser.add_argument("--type", "-t", help="基金类型筛选")
    args = parser.parse_args()

    try:
        if args.command == "history":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = quote_history(args.code)
        elif args.command == "history_multi":
            if not args.code:
                result = {"error": "需要 --code 参数（多个用逗号分隔）"}
            else:
                codes = args.code.split(",")
                result = quote_history_multi(codes)
        elif args.command == "position":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = invest_position(args.code)
        elif args.command == "industry":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = industry_distribution(args.code)
        elif args.command == "manager":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = fund_manager(args.code)
        elif args.command == "period":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = period_change(args.code)
        elif args.command == "info":
            if not args.code:
                result = {"error": "需要 --code 参数"}
            else:
                result = fund_base_info(args.code)
        elif args.command == "codes":
            result = fund_codes(args.type)
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
