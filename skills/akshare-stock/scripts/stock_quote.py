#!/usr/bin/env python3
"""
Get real-time stock quote for A-share stocks.

Usage:
    python stock_quote.py <stock_code>

Example:
    python stock_quote.py 600519

Stock code format:
    - Shanghai: 600000
    - Shenzhen: 000001
    - ChiNext: 300001
    - STAR Market: 688001
"""

import pandas as pd
import sys
import akshare as ak
import json


def get_quote(stock_code):
    try:
        # Determine exchange prefix
        if stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"

        # Get real-time quote
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == stock_code]

        if stock.empty:
            print(f"[ERROR] Stock code {stock_code} not found")
            sys.exit(1)

        row = stock.iloc[0]

        result = {
            "code": stock_code,
            "name": row['名称'],
            "price": float(row['最新价']) if pd.notna(row['最新价']) else None,
            "change": float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else None,
            "change_amount": float(row['涨跌额']) if pd.notna(row['涨跌额']) else None,
            "volume": int(row['成交量']) if pd.notna(row['成交量']) else None,
            "amount": float(row['成交额']) if pd.notna(row['成交额']) else None,
            "open": float(row['今开']) if pd.notna(row['今开']) else None,
            "high": float(row['最高']) if pd.notna(row['最高']) else None,
            "low": float(row['最低']) if pd.notna(row['最低']) else None,
            "pre_close": float(row['昨收']) if pd.notna(row['昨收']) else None,
            "pe": float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else None,
            "pb": float(row['市净率']) if pd.notna(row['市净率']) else None,
            "market_cap": float(row['总市值']) if pd.notna(row['总市值']) else None,
            "float_cap": float(row['流通市值']) if pd.notna(row['流通市值']) else None,
        }

        # Print readable format
        print(f"\n📈 {result['name']} ({stock_code})")
        print(f"{'=' *40}")
        print(f"  最新价: {result['price']}")
        if result['change'] is not None:
            emoji = "📈" if result['change'] >= 0 else "📉"
            print(f"  涨跌幅: {emoji} {result['change']:.2f}%")
        print(f"  涨跌额: {result['change_amount']}")
        print(f"  成交量: {result['volume']}")
        print(f"  成交额: {result['amount']}")
        print(f"  今开: {result['open']}")
        print(f"  最高: {result['high']}")
        print(f"  最低: {result['low']}")
        print(f"  昨收: {result['pre_close']}")
        print(f"  市盈率: {result['pe']}")
        print(f"  市净率: {result['pb']}")
        print(f"  总市值: {result['market_cap']}")
        print(f"  流通市值: {result['float_cap']}")

        # Print JSON for parsing
        print(f"\n  # QUOTE_META##")
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Failed to get quote: {e}")
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python stock_quote.py <stock_code>")
        print("Example: python stock_quote.py 600519")
        sys.exit(1)

    stock_code = sys.argv[1]
    get_quote(stock_code)
