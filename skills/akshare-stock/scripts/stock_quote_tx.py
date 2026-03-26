#!/usr/bin/env python3
"""
Get real-time stock quote for A-share stocks (Tencent Finance API).

Usage:
    python stock_quote_tx.py <stock_code>

Example:
    python stock_quote_tx.py 600519
"""

import json
import requests
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



def get_quote_tx(stock_code):
    try:
        # Determine exchange prefix
        if stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"

        # Tencent Finance API
        url = f"https://qt.gtimg.cn/q={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gbk'  # Tencent uses GBK encoding

        data = resp.text
        if not data or '~' not in data:
            print(f"[ERROR] No data for {stock_code}")
            sys.exit(1)

        # Parse Tencent format: v_sh600519="1~贵州茅台~600519..."
        content = data.split('"')[1]
        fields = content.split('~')

        # Field mapping based on Tencent format
        result = {
            "code": fields[2] if len(fields) > 2 else stock_code,
            "name": fields[1] if len(fields) > 1 else "Unknown",
            "price": float(fields[3]) if len(fields) > 3 and fields[3] else 0,
            "pre_close": float(fields[4]) if len(fields) > 4 and fields[4] else 0,
            "open": float(fields[5]) if len(fields) > 5 and fields[5] else 0,
            "volume": int(fields[6]) if len(fields) > 6 and fields[6] else 0,
            "volume_inner": int(fields[7]) if len(fields) > 7 and fields[7] else 0,
            "volume_outer": int(fields[8]) if len(fields) > 8 and fields[8] else 0,
            "bid1": float(fields[9]) if len(fields) > 9 and fields[9] else 0,
            "bid1_vol": int(fields[10]) if len(fields) > 10 and fields[10] else 0,
            "ask1": float(fields[19]) if len(fields) > 19 and fields[19] else 0,
            "ask1_vol": int(fields[20]) if len(fields) > 20 and fields[20] else 0,
            "high": float(fields[33]) if len(fields) > 33 and fields[33] else 0,
            "low": float(fields[34]) if len(fields) > 34 and fields[34] else 0,
            "change": float(fields[31]) if len(fields) > 31 and fields[31] else 0,
            "change_pct": float(fields[32]) if len(fields) > 32 and fields[32] else 0,
            "amount": float(fields[37]) if len(fields) > 37 and fields[37] else 0,
            "pe": float(fields[39]) if len(fields) > 39 and fields[39] else 0,
            "pb": float(fields[46]) if len(fields) > 46 and fields[46] else 0,
            "market_cap": float(fields[44]) if len(fields) > 44 and fields[44] else 0,
            "float_cap": float(fields[45]) if len(fields) > 45 and fields[45] else 0,
            "turnover": float(fields[38]) if len(fields) > 38 and fields[38] else 0,
        }

        # Print readable format
        change_emoji = "📈" if result['change'] >= 0 else "📉"
        print(f"\n📈 {result['name']} ({result['code']})")
        print(f"{'='*50}")
        print(f"  最新价: {result['price']:.2f}")
        print(f"  涨跌幅: {change_emoji} {result['change_pct']:.2f}%")
        print(f"  涨跌额: {result['change']:.2f}")
        print(f"  成交量: {result['volume']:,}")
        print(f"  成交额: {result['amount']/10000:.2f}万")
        print(f"  今开: {result['open']:.2f}")
        print(f"  最高: {result['high']:.2f}")
        print(f"  最低: {result['low']:.2f}")
        print(f"  昨收: {result['pre_close']:.2f}")
        print(f"  买一: {result['bid1']:.2f} ({result['bid1_vol']})")
        print(f"  卖一: {result['ask1']:.2f} ({result['ask1_vol']})")
        print(f"  市盈率: {result['pe']:.2f}")
        print(f"  市净率: {result['pb']:.2f}")
        print(f"  总市值: {result['market_cap']/10000:.2f}亿")
        print(f"  流通市值: {result['float_cap']/10000:.2f}亿")
        print(f"  换手率: {result['turnover']:.2f}%")

        # Print JSON for parsing
        print(f"\n##QUOTE_META##")
        print(json.dumps(result, ensure_ascii=False, default=str))

    except Exception as e:
        print(f"[ERROR] Failed to get quote: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stock_quote_tx.py <stock_code>")
        print("Example: python stock_quote_tx.py 600519")
        sys.exit(1)

    stock_code = sys.argv[1]
    get_quote_tx(stock_code)
