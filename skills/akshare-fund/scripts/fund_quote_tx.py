#!/usr/bin/env python3
"""
Get real-time fund quote (ETF/LOF) via Tencent Finance API.

Usage:
    python fund_quote_tx.py <fund_code>

Example:
    python fund_quote_tx.py 510300
    python fund_quote_tx.py 512800

Fund code format:
    - ETF: 510300 (沪深300ETF), 512800 (银行ETF)
    - LOF: 160106 (南方高增)
"""

import sys
import json
import requests

def get_fund_quote_tx(fund_code):
    try:
        # Tencent Finance API for funds (ETF/LOF use same format as stocks)
        # Determine exchange prefix
        if fund_code.startswith('5'):
            symbol = f"sh{fund_code}"
        elif fund_code.startswith('1') or fund_code.startswith('0'):
            symbol = f"sz{fund_code}"
        else:
            symbol = fund_code
        
        url = f"https://qt.gtimg.cn/q={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gbk'
        
        data = resp.text
        if not data or '~' not in data:
            print(f"[ERROR] No data for fund {fund_code}")
            sys.exit(1)
        
        # Parse Tencent format: v_fu_510300="1~300ETF~510300..."
        content = data.split('"')[1]
        fields = content.split('~')
        
        # Field mapping for funds
        result = {
            "code": fields[2] if len(fields) > 2 else fund_code,
            "name": fields[1] if len(fields) > 1 else "Unknown",
            "price": float(fields[3]) if len(fields) > 3 and fields[3] else 0,
            "pre_close": float(fields[4]) if len(fields) > 4 and fields[4] else 0,
            "open": float(fields[5]) if len(fields) > 5 and fields[5] else 0,
            "high": float(fields[33]) if len(fields) > 33 and fields[33] else 0,
            "low": float(fields[34]) if len(fields) > 34 and fields[34] else 0,
            "change": float(fields[31]) if len(fields) > 31 and fields[31] else 0,
            "change_pct": float(fields[32]) if len(fields) > 32 and fields[32] else 0,
            "volume": int(fields[36]) if len(fields) > 36 and fields[36] else 0,
            "amount": float(fields[37]) if len(fields) > 37 and fields[37] else 0,
            "iopv": float(fields[46]) if len(fields) > 46 and fields[46] else 0,  # IOPV for ETF
            "discount": float(fields[47]) if len(fields) > 47 and fields[47] else 0,  # Discount/Premium
        }
        
        # Print readable format
        change_emoji = "📈" if result['change'] >= 0 else "📉"
        print(f"\n📊 {result['name']} ({result['code']})")
        print(f"{'='*50}")
        print(f"  最新价: {result['price']:.3f}")
        if result['change_pct'] is not None:
            print(f"  涨跌幅: {change_emoji} {result['change_pct']:.2f}%")
        print(f"  涨跌额: {result['change']:.3f}")
        print(f"  今开: {result['open']:.3f}")
        print(f"  最高: {result['high']:.3f}")
        print(f"  最低: {result['low']:.3f}")
        print(f"  昨收: {result['pre_close']:.3f}")
        print(f"  成交量: {result['volume']:,}")
        print(f"  成交额: {result['amount']/10000:.2f}万")
        if result['iopv']:
            print(f"  IOPV: {result['iopv']:.3f}")
        if result['discount']:
            premium_emoji = "🔴" if result['discount'] > 0 else "🟢"
            print(f"  折溢价: {premium_emoji} {result['discount']:.2f}%")
        
        # Print JSON for parsing
        print(f"\n##FUND_META##")
        print(json.dumps(result, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get fund quote: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fund_quote_tx.py <fund_code>")
        print("Example: python fund_quote_tx.py 510300")
        print("         python fund_quote_tx.py 512800")
        sys.exit(1)
    
    fund_code = sys.argv[1]
    get_fund_quote_tx(fund_code)
