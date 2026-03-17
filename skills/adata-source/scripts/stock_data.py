#!/usr/bin/env python3
"""adata 股票数据获取脚本"""
import sys
import json
import argparse
import adata
import pandas as pd


def _df_to_json(df, max_rows=None):
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return []
    if max_rows and len(df) > max_rows:
        df = df.head(max_rows)
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def stock_list():
    """全部A股列表"""
    df = adata.stock.info.all_code()
    return {"count": len(df), "data": _df_to_json(df)}


def market(code, start_date=None):
    """个股日线行情"""
    kw = {"stock_code": code}
    if start_date:
        kw["start_date"] = start_date
    df = adata.stock.market.get_market(**kw)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def market_min(code):
    """个股分钟级行情"""
    df = adata.stock.market.get_market_min(stock_code=code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def capital_flow(code):
    """个股资金流向"""
    df = adata.stock.market.get_capital_flow(stock_code=code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def capital_flow_min(code):
    """个股分钟级资金流"""
    df = adata.stock.market.get_capital_flow_min(stock_code=code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def core_finance(code):
    """核心财务指标（43个字段）"""
    df = adata.stock.finance.get_core_index(stock_code=code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def dividend(code):
    """分红数据"""
    df = adata.stock.market.get_dividend(stock_code=code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def list_current():
    """全市场实时行情"""
    try:
        df = adata.stock.market.list_market_current()
        return {"count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"实时行情获取失败: {str(e)}"}


def concept_members(concept_code):
    """概念板块成分股"""
    try:
        df = adata.stock.info.concept_constituent_east(concept_code=concept_code)
        return {"concept": concept_code, "count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"error": str(e)}


def index_members(index_code):
    """指数成分股"""
    try:
        df = adata.stock.info.index_constituent(index_code=index_code)
        return {"index": index_code, "count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"error": str(e)}


def market_index(index_code, start_date=None):
    """指数行情"""
    kw = {"index_code": index_code}
    if start_date:
        kw["start_date"] = start_date
    df = adata.stock.market.get_market_index(**kw)
    return {"index": index_code, "count": len(df), "data": _df_to_json(df)}


def trade_calendar():
    """交易日历"""
    df = adata.stock.info.trade_calendar()
    return {"count": len(df), "data": _df_to_json(df)}


def stock_shares(code):
    """股本结构"""
    try:
        df = adata.stock.info.get_stock_shares(stock_code=code)
        return {"code": code, "count": len(df), "data": _df_to_json(df)}
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="adata 股票数据")
    parser.add_argument("command", choices=[
        "list", "market", "market_min", "capital", "capital_min",
        "finance", "dividend", "current", "concept_members",
        "index_members", "index_market", "calendar", "shares"
    ])
    parser.add_argument("--code", "-c", help="股票/指数/概念代码")
    parser.add_argument("--start", "-s", help="开始日期 YYYY-MM-DD")
    parser.add_argument("--concept", help="概念板块代码")
    parser.add_argument("--index", help="指数代码")
    args = parser.parse_args()

    try:
        if args.command == "list":
            result = stock_list()
        elif args.command == "market":
            result = market(args.code, args.start) if args.code else {"error": "需要 --code"}
        elif args.command == "market_min":
            result = market_min(args.code) if args.code else {"error": "需要 --code"}
        elif args.command == "capital":
            result = capital_flow(args.code) if args.code else {"error": "需要 --code"}
        elif args.command == "capital_min":
            result = capital_flow_min(args.code) if args.code else {"error": "需要 --code"}
        elif args.command == "finance":
            result = core_finance(args.code) if args.code else {"error": "需要 --code"}
        elif args.command == "dividend":
            result = dividend(args.code) if args.code else {"error": "需要 --code"}
        elif args.command == "current":
            result = list_current()
        elif args.command == "concept_members":
            code = args.concept or args.code
            result = concept_members(code) if code else {"error": "需要 --concept 或 --code"}
        elif args.command == "index_members":
            code = args.index or args.code
            result = index_members(code) if code else {"error": "需要 --index 或 --code"}
        elif args.command == "index_market":
            code = args.index or args.code
            result = market_index(code, args.start) if code else {"error": "需要 --index 或 --code"}
        elif args.command == "calendar":
            result = trade_calendar()
        elif args.command == "shares":
            result = stock_shares(args.code) if args.code else {"error": "需要 --code"}
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
