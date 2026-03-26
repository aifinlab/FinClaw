#!/usr/bin/env python3
"""
Get real-time stock quotes via 智兔数服 (Zhitu API).

Usage:
    python zhitu_quote.py <code>

Example:
    python zhitu_quote.py 000001
    python zhitu_quote.py 600519.SH
    python zhitu_quote.py 00700.HK

Stock code format:
    000001 - Shenzhen A-share
    600000.SH - Shanghai A-share
    300001 - ChiNext
    688001 - STAR Market
    00001.HK - Hong Kong
    510300 - Fund/ETF
"""

import json
import os
import requests
import sys

API_BASE = "http://api.zhituapi.com"
TOKEN = os.environ.get("ZHITU_API_TOKEN", "")

def get_quote(code):
    # Normalize code
    code = code.upper()
    if '.' not in code:
        # Auto-detect exchange
        if code.startswith('6') or code.startswith('688'):
            code = code + '.SH'
        elif code.startswith('0') or code.startswith('3'):
            code = code + '.SZ'
        elif code.startswith('4') or code.startswith('8'):
            code = code + '.BJ'

    try:
        # Determine market type
        if '.HK' in code:
            # Hong Kong stocks
            url = f"{API_BASE}/hk/stock/real/ssjy/{code.replace('.HK', '')}?token={TOKEN}"
        elif code.startswith('5') or code.startswith('1'):
            # Fund/ETF - treat as A-share
            url = f"{API_BASE}/hs/custom/realall?token={TOKEN}"
            # For funds, we need to check the specific endpoint
            fund_code = code.replace('.SH', '').replace('.SZ', '')
            url = f"{API_BASE}/fund/real/ssjy/{fund_code}?token={TOKEN}"
        else:
            # A-shares
            url = f"{API_BASE}/hs/custom/realall?token={TOKEN}"

        print(f"\n📈 Real-time Quote - {code}")
        print(f"{'='*70}\n")

        resp = requests.get(url, timeout=10)
        data = resp.json()

        # For custom/realall, we need to filter
        if 'data' in str(type(data)):
            # Direct response
            result = data
        else:
            result = data

        # Parse and display
        if isinstance(result, dict):
            print(f"  Code: {code}")

            # Common fields
            fields_map = {
                'p': 'Price',
                'c': 'Code',
                'n': 'Name',
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'yc': 'Previous Close',
                'v': 'Volume',
                'cje': 'Amount',
                'zf': 'Amplitude',
                'tr': 'Turnover',
                'pe': 'P/E',
                'pb': 'P/B',
                't': 'Time'
            }

            for key, label in fields_map.items():
                if key in result:
                    value = result[key]
                    if key in ['p', 'o', 'h', 'l', 'yc']:
                        print(f"  {label:<15}: {value:.2f}")
                    elif key == 'cje':
                        print(f"  {label:<15}: {value/10000:.2f}万")
                    elif key == 'v':
                        print(f"  {label:<15}: {value:,}")
                    elif key == 'zf':
                        print(f"  {label:<15}: {value:.2f}%")
                    else:
                        print(f"  {label:<15}: {value}")

            # Print JSON for parsing
            print(f"\n##QUOTE_META##")
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"  Data: {result}")

    except Exception as e:
        print(f"[ERROR] Failed to get quote: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zhitu_quote.py <code>")
        print("Example: python zhitu_quote.py 000001")
        print("         python zhitu_quote.py 600519.SH")
        print("         python zhitu_quote.py 00700.HK")
        sys.exit(1)

    code = sys.argv[1]
    get_quote(code)
