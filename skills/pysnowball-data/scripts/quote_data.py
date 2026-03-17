#!/usr/bin/env python3
"""pysnowball 行情数据（无需 token）"""
import sys
import json
import argparse
import pysnowball as ball


def quotec(codes):
    """获取实时行情快照（支持 A/港/美）
    codes: 逗号分隔的股票代码，如 SH600519,SZ000001,HK00700
    """
    try:
        result = ball.quotec(codes)
        if isinstance(result, dict) and "data" in result:
            data = result["data"]
            # 精简输出
            clean = []
            for item in (data or []):
                clean.append({
                    "symbol": item.get("symbol"),
                    "current": item.get("current"),
                    "percent": item.get("percent"),
                    "chg": item.get("chg"),
                    "volume": item.get("volume"),
                    "amount": item.get("amount"),
                    "market_capital": item.get("market_capital"),
                    "float_market_capital": item.get("float_market_capital"),
                    "turnover_rate": item.get("turnover_rate"),
                    "amplitude": item.get("amplitude"),
                    "open": item.get("open"),
                    "last_close": item.get("last_close"),
                    "high": item.get("high"),
                    "low": item.get("low"),
                    "avg_price": item.get("avg_price"),
                    "current_year_percent": item.get("current_year_percent"),
                    "is_trade": item.get("is_trade"),
                })
            return {"count": len(clean), "data": clean}
        return {"count": 0, "data": [], "raw": result}
    except Exception as e:
        return {"count": 0, "data": [], "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="pysnowball 行情数据（无需token）")
    parser.add_argument("command", choices=["quotec"])
    parser.add_argument("--code", "-c", required=True, help="股票代码（逗号分隔），如 SH600519,SZ000001,HK00700")
    args = parser.parse_args()

    if args.command == "quotec":
        result = quotec(args.code)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
