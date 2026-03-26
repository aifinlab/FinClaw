#!/usr/bin/env python3
"""pysnowball 财务和高级数据（需要 token）
使用前需设置 token：
import argparse
  ball.set_token('xq_a_token=你的token;')
或通过 --token 参数传入
"""
import json
import pysnowball as ball
import pysnowball as ball
import sys


def _safe_call(func, *args, **kwargs):
    """安全调用，处理 token 缺失等错误"""
    try:
        result = func(*args, **kwargs)
        if isinstance(result, str):
            result = json.loads(result)
        return result
    except Exception as e:
        err_msg = str(e)
        if "TOKEN" in err_msg or "token" in err_msg:
            return {"error": "未设置 token。请先通过 --token 传入雪球 token，或在脚本中调用 ball.set_token()"}
        return {"error": err_msg}


def income(code):
    """利润表"""
    return _safe_call(ball.income, code)


def balance(code):
    """资产负债表"""
    return _safe_call(ball.balance, code)


def cashflow(code):
    """现金流量表"""
    return _safe_call(ball.cash_flow, code)


def indicator(code):
    """核心财务指标"""
    return _safe_call(ball.indicator, code)


def kline(code, period="day"):
    """K线数据"""
    return _safe_call(ball.kline, code, period=period)


def capital_flow(code):
    """资金流向"""
    return _safe_call(ball.capital_flow, code)


def industry_compare(code):
    """行业对比"""
    return _safe_call(ball.industry_compare, code)


def holders(code):
    """机构持仓变动"""
    return _safe_call(ball.org_holding_change, code)


def top_holders(code):
    """十大股东"""
    return _safe_call(ball.top_holders, code)


def earningforecast(code):
    """盈利预测"""
    return _safe_call(ball.earningforecast, code)


def business_analysis(code):
    """业务分析"""
    return _safe_call(ball.business_analysis, code)


def main():
    parser = argparse.ArgumentParser(description="pysnowball 财务数据（需token）")
    parser.add_argument("command", choices=[
        "income", "balance", "cashflow", "indicator",
        "kline", "capital", "industry", "holders",
        "top_holders", "forecast", "business"
    ])
    parser.add_argument("--code", "-c", required=True, help="股票代码，如 SH600519")
    parser.add_argument("--period", "-p", default="day", help="K线周期: day/week/month")
    parser.add_argument("--token", "-t", help="雪球 xq_a_token")
    args = parser.parse_args()

    if args.token:
        ball.set_token(f'xq_a_token={args.token};')

    cmd_map = {
        "income": lambda: income(args.code),
        "balance": lambda: balance(args.code),
        "cashflow": lambda: cashflow(args.code),
        "indicator": lambda: indicator(args.code),
        "kline": lambda: kline(args.code, args.period),
        "capital": lambda: capital_flow(args.code),
        "industry": lambda: industry_compare(args.code),
        "holders": lambda: holders(args.code),
        "top_holders": lambda: top_holders(args.code),
        "forecast": lambda: earningforecast(args.code),
        "business": lambda: business_analysis(args.code),
    }

    result = cmd_map[args.command]()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
