#!/usr/bin/env python3
"""获取股票实时价格和K线数据"""
import akshare as ak
import json
import sys


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data



def get_stock_price(symbol, period="daily", start_date=None):
    """获取股票价格"""
    try:
        df = ak.stock_zh_kline(
            symbol=symbol,
            period=period,
            adjust="qfq",
            start_date=start_date
        )
        latest = df.iloc[-1]
        return {
            "symbol": symbol,
            "date": str(latest['date']),
            "open": float(latest['open']),
            "high": float(latest['high']),
            "low": float(latest['low']),
            "close": float(latest['close']),
            "volume": int(latest['volume']),
            "pct_chg": float(latest['pct_chg'])
        }
    except Exception as e:
        return {"error": str(e)}

def get_market_overview():
    """获取大盘概览"""
    try:
        df = ak.stock_zh_a_spot_em()
        # 涨跌幅排行
        top_gainers = df.nlargest(5, '涨跌幅')[['代码', '名称', '涨跌幅']].to_dict('records')
        top_losers = df.nsmallest(5, '涨跌幅')[['代码', '名称', '涨跌幅']].to_dict('records')
        return {
            "total_stocks": len(df),
            "top_gainers": top_gainers,
            "top_losers": top_losers
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "price":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "000001"
            result = get_stock_price(symbol)
        elif cmd == "overview":
            result = get_market_overview()
        else:
            result = {"error": f"Unknown command: {cmd}"}
    else:
        result = {"usage": "python stock.py price <symbol> | overview"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
