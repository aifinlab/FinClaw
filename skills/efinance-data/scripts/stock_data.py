#!/usr/bin/env python3
"""
efinance 股票数据获取脚本
支持：实时行情、历史K线、基本信息、十大股东、资金流向、龙虎榜、业绩报表
"""
import sys
import json
import argparse
from datetime import datetime, timedelta

import efinance as ef
import pandas as pd


def _df_to_json(df, max_rows=None):
    """DataFrame 转 JSON，处理 NaN 和类型"""
    if df is None or df.empty:
        return []
    if max_rows:
        df = df.head(max_rows)
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def realtime_quotes(codes=None):
    """获取实时行情
    codes: 股票代码列表，为空则返回全市场
    返回字段：代码、名称、最新价、涨跌幅、换手率、动态PE、总市值、流通市值等
    注意：非交易时段（周末、节假日、盘前盘后）可能返回空数据
    """
    try:
        df = ef.stock.get_realtime_quotes()
    except Exception as e:
        return {"count": 0, "data": [], "warning": f"实时行情获取失败（可能处于非交易时段）: {str(e)}"}
    if df is None or df.empty:
        return {"count": 0, "data": [], "warning": "当前无实时行情数据（可能处于非交易时段）"}
    if codes:
        df = df[df["股票代码"].isin(codes)]
    cols = ["股票代码", "股票名称", "最新价", "涨跌幅", "涨跌额", "今开", "最高", "最低",
            "昨日收盘", "成交量", "成交额", "换手率", "量比", "动态市盈率", "总市值", "流通市值"]
    available = [c for c in cols if c in df.columns]
    return {"count": len(df), "data": _df_to_json(df[available])}


def quote_history(code, period="daily", start_date=None, end_date=None):
    """获取历史K线
    code: 股票代码
    period: daily/weekly/monthly
    """
    kw = {}
    if start_date:
        kw["beg"] = start_date
    if end_date:
        kw["end"] = end_date
    ktype_map = {"daily": 101, "weekly": 102, "monthly": 103,
                 "5min": 5, "15min": 15, "30min": 30, "60min": 60}
    ktype = ktype_map.get(period, 101)
    df = ef.stock.get_quote_history(code, klt=ktype, **kw)
    return {"code": code, "period": period, "count": len(df), "data": _df_to_json(df)}


def base_info(code):
    """获取个股基本信息：净利润、市值、行业、PE、PB、ROE、毛利率、净利率"""
    info = ef.stock.get_base_info(code)
    if isinstance(info, pd.Series):
        return info.to_dict()
    return {"error": "未获取到数据"}


def top10_holders(code):
    """获取十大股东信息"""
    df = ef.stock.get_top10_stock_holder_info(code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def history_bill(code, days=30):
    """获取个股资金流向（主力/大单/超大单净流入）"""
    df = ef.stock.get_history_bill(code)
    if days and len(df) > days:
        df = df.tail(days)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def today_bill(code):
    """获取个股当日分时资金流"""
    df = ef.stock.get_today_bill(code)
    return {"code": code, "count": len(df), "data": _df_to_json(df)}


def daily_billboard():
    """获取龙虎榜数据"""
    df = ef.stock.get_daily_billboard()
    return {"count": len(df), "data": _df_to_json(df)}


def company_performance():
    """获取最新业绩报表（全市场）
    包含：营收、净利润、同比增长、ROE、毛利率、每股收益等
    """
    df = ef.stock.get_all_company_performance()
    return {"count": len(df), "data": _df_to_json(df)}


def latest_holder_number(code):
    """获取最新股东人数"""
    df = ef.stock.get_latest_holder_number(code)
    if isinstance(df, pd.DataFrame) and not df.empty:
        return {"code": code, "data": _df_to_json(df)}
    return {"code": code, "data": []}


def latest_ipo_info():
    """获取最新IPO/新股信息"""
    df = ef.stock.get_latest_ipo_info()
    return {"count": len(df), "data": _df_to_json(df)}


def belong_board(code):
    """获取个股所属板块"""
    df = ef.stock.get_belong_board(code)
    if isinstance(df, pd.DataFrame) and not df.empty:
        return {"code": code, "data": _df_to_json(df)}
    return {"code": code, "data": []}


def deal_detail(code, max_rows=500):
    """获取逐笔成交明细（默认最近500笔）"""
    df = ef.stock.get_deal_detail(code)
    return {"code": code, "count": len(df), "data": _df_to_json(df, max_rows=max_rows)}


COMMANDS = {
    "realtime": realtime_quotes,
    "history": quote_history,
    "info": base_info,
    "holders": top10_holders,
    "bill": history_bill,
    "today_bill": today_bill,
    "billboard": daily_billboard,
    "performance": company_performance,
    "holder_number": latest_holder_number,
    "ipo": latest_ipo_info,
    "board": belong_board,
    "deals": deal_detail,
}


def main():
    parser = argparse.ArgumentParser(description="efinance 股票数据获取")
    parser.add_argument("command", choices=COMMANDS.keys(), help="数据类型")
    parser.add_argument("--code", "-c", help="股票代码，多个用逗号分隔")
    parser.add_argument("--period", "-p", default="daily", help="K线周期: daily/weekly/monthly/5min/15min/30min/60min")
    parser.add_argument("--start", "-s", help="开始日期 YYYYMMDD")
    parser.add_argument("--end", "-e", help="结束日期 YYYYMMDD")
    parser.add_argument("--days", "-d", type=int, default=30, help="资金流天数")
    parser.add_argument("--max-rows", type=int, help="最大返回行数")
    args = parser.parse_args()

    try:
        if args.command == "realtime":
            codes = args.code.split(",") if args.code else None
            result = realtime_quotes(codes)
        elif args.command == "history":
            if not args.code:
                result = {"error": "history 需要 --code 参数"}
            else:
                result = quote_history(args.code, args.period, args.start, args.end)
        elif args.command in ("info", "holders", "holder_number", "board"):
            if not args.code:
                result = {"error": f"{args.command} 需要 --code 参数"}
            else:
                result = COMMANDS[args.command](args.code)
        elif args.command == "bill":
            if not args.code:
                result = {"error": "bill 需要 --code 参数"}
            else:
                result = history_bill(args.code, args.days)
        elif args.command == "today_bill":
            if not args.code:
                result = {"error": "today_bill 需要 --code 参数"}
            else:
                result = today_bill(args.code)
        elif args.command == "deals":
            if not args.code:
                result = {"error": "deals 需要 --code 参数"}
            else:
                result = deal_detail(args.code, args.max_rows or 500)
        else:
            result = COMMANDS[args.command]()
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
