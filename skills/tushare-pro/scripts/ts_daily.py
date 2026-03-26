#!/usr/bin/env python3
"""
Get daily market data via Tushare Pro.

Usage:
    python ts_daily.py <ts_code> [start_date] [end_date]

Example:
    python ts_daily.py 600519.SH 20240101 20240312
    python ts_daily.py 000001.SZ

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

from datetime import datetime, timedelta
import json
import os
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



def get_daily(ts_code, start_date=None, end_date=None):
    try:
        import tushare as ts
    except ImportError:
        print("[ERROR] tushare not installed. Run: pip install tushare")
        sys.exit(1)

    token = os.environ.get('TUSHARE_TOKEN')
    if not token:
        print("[ERROR] TUSHARE_TOKEN not set")
        sys.exit(1)

    try:
        pro = ts.pro_api(token)

        # Set default dates
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

        # Query daily data
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

        if df.empty:
            print(f"[INFO] No daily data for {ts_code}")
            sys.exit(0)

        print(f"\n📈 Daily Market Data - {ts_code}")
        print(f"{'='*80}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Total records: {len(df)}\n")

        print(f"  {'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Change%':>10}")
        print(f"  {'-'*80}")

        results = []
        for _, row in df.iterrows():
            result = {
                'trade_date': row.get('trade_date', 'N/A'),
                'open': row.get('open', 0),
                'high': row.get('high', 0),
                'low': row.get('low', 0),
                'close': row.get('close', 0),
                'pre_close': row.get('pre_close', 0),
                'change': row.get('change', 0),
                'pct_chg': row.get('pct_chg', 0),
                'vol': row.get('vol', 0),
                'amount': row.get('amount', 0)
            }

            change_emoji = "📈" if result['pct_chg'] >= 0 else "📉"
            print(f"  {result['trade_date']:<12} {result['open']:>10.2f} {result['high']:>10.2f} {result['low']:>10.2f} {result['close']:>10.2f} {change_emoji}{result['pct_chg']:>8.2f}%")

            results.append(result)

        # Summary
        if results:
            closes = [r['close'] for r in results]
            print(f"\n  Summary:")
            print(f"    Highest: {max(r['high'] for r in results):.2f}")
            print(f"    Lowest:  {min(r['low'] for r in results):.2f}")
            print(f"    Return:  {((closes[-1] - closes[0]) / closes[0] * 100):.2f}%")

        # Print JSON for parsing
        print(f"\n##DAILY_META##")
        print(json.dumps({
            'ts_code': ts_code,
            'count': len(results),
            'data': results
        }, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts_daily.py <ts_code> [start_date] [end_date]")
        print("Example: python ts_daily.py 600519.SH 20240101 20240312")
        sys.exit(1)

    ts_code = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None

    get_daily(ts_code, start_date, end_date)
