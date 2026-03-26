#!/usr/bin/env python3
"""
Get historical K-line data via 智兔数服 (Zhitu API).

Usage:
    python zhitu_hist.py <code> [start_date] [end_date]

Example:
    python zhitu_hist.py 000001 20240101 20240312
    python zhitu_hist.py 600519.SH 2024-01-01 2024-03-12

Arguments:
    code: Stock code (e.g., 000001, 600519.SH)
    start_date: Start date (YYYYMMDD or YYYY-MM-DD)
    end_date: End date (YYYYMMDD or YYYY-MM-DD)
"""

from datetime import datetime, timedelta
import json
import os
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



API_BASE = "https://api.zhituapi.com"
TOKEN = os.environ.get("ZHITU_API_TOKEN", "")

def get_history(code, start_date=None, end_date=None):
    # Normalize code
    code = code.upper()
    if '.' not in code:
        if code.startswith('6') or code.startswith('688'):
            code = code + '.SH'
        elif code.startswith('0') or code.startswith('3'):
            code = code + '.SZ'
        elif code.startswith('4') or code.startswith('8'):
            code = code + '.BJ'

    # Normalize dates
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')

    # Remove dashes from dates
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')

    try:
        url = f"{API_BASE}/hs/history/{code}/d/n?token={TOKEN}&st={start_date}&et={end_date}"

        print(f"\n📊 Historical Data - {code}")
        print(f"Period: {start_date} to {end_date}\n")
        print(f"{'='*80}")

        resp = requests.get(url, timeout=10)
        data = resp.json()

        if not isinstance(data, list) or len(data) == 0:
            print(f"[INFO] No data found for {code}")
            sys.exit(0)

        # Display header
        print(f"  {'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>15}")
        print(f"  {'-'*80}")

        results = []
        for item in data:
            row = {
                'date': item.get('d', 'N/A'),
                'open': float(item.get('o', 0)),
                'high': float(item.get('h', 0)),
                'low': float(item.get('l', 0)),
                'close': float(item.get('c', 0)),
                'volume': int(item.get('v', 0))
            }

            results.append(row)

            # Show only last 15 rows
            if len(results) > len(data) - 15:
                print(f"  {row['date']:<12} {row['open']:>10.2f} {row['high']:>10.2f} {row['low']:>10.2f} {row['close']:>10.2f} {row['volume']:>15,}")

        # Statistics
        if results:
            closes = [r['close'] for r in results]
            print(f"\n  {'='*80}")
            print(f"  Statistics ({len(results)} trading days):")
            print(f"    Highest: {max(r['high'] for r in results):.2f}")
            print(f"    Lowest:  {min(r['low'] for r in results):.2f}")
            print(f"    Return:  {((closes[-1] - closes[0]) / closes[0] * 100):.2f}%")

        # Print JSON for parsing
        print(f"\n##HIST_META##")
        print(json.dumps({
            'code': code,
            'count': len(results),
            'data': results
        }, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zhitu_hist.py <code> [start_date] [end_date]")
        print("Example: python zhitu_hist.py 000001 20240101 20240312")
        sys.exit(1)

    code = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None

    get_history(code, start_date, end_date)
