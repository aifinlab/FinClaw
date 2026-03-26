#!/usr/bin/env python3
"""
Get historical price data for A-share stocks.

Usage:
    python stock_hist.py <stock_code> [days]

Example:
    python stock_hist.py 600519 30

Arguments:
    stock_code: 6-digit stock code
    days: Number of days (default: 30, max: 365)
"""

import sys
from datetime import datetime, timedelta
import akshare as ak
import json


def get_history(stock_code, days=30):
    try:
        # Get stock name first
        df_spot = ak.stock_zh_a_spot_em()
        stock_info = df_spot[df_spot['代码'] == stock_code]

        if stock_info.empty:
            print(f"[ERROR] Stock code {stock_code} not found")
            sys.exit(1)

        stock_name = stock_info.iloc[0]['名称']

        # Calculate date range
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        # Get historical data
        df = ak.stock_zh_a_hist(
    symbol=stock_code,
    period="daily",
    start_date=start_date,
    end_date=end_date,
        adjust="qfq")

        if df.empty:
            print(f"[ERROR] No historical data for {stock_code}")
            sys.exit(1)

        # Convert to list of dicts
        records = []
        for _, row in df.iterrows():
            records.append({
                "date": row['日期'],
                "open": float(row['开盘']),
                "close": float(row['收盘']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "volume": int(row['成交量']),
                "amount": float(row['成交额']),
                "amplitude": float(row['振幅']),
                "change_pct": float(row['涨跌幅']),
                "change": float(row['涨跌额']),
                "turnover": float(row['换手率'])
            })

        # Print readable format
        print(f"\n📊 {stock_name} ({stock_code}) - Historical Data")
        print(f"{'=' *60}")
        print(f"  Period: {records[0]['date']} to {records[-1]['date']}")
        print(f"  Total days: {len(records)}\n")

        # Print recent 10 days
        print("  Recent 10 days:")
        print(
    f"  {
        'Date':^12} {
            'Open':^8} {
                'Close':^8} {
                    'High':^8} {
                        'Low':^8} {
                            'Change%':^8}")
        print(f"  {'-' *60}")
        for r in records[-10:]:
            change_emoji = "📈" if r['change_pct'] >= 0 else "📉"
            print(
    f"  {
        r['date']:^12} {
            r['open']:>8.2f} {
                r['close']:>8.2f} {
                    r['high']:>8.2f} {
                        r['low']:>8.2f} {change_emoji}{
                            r['change_pct']:>6.2f}%")

        # Calculate stats
        closes = [r['close'] for r in records]
        print(f"\n  Statistics:")
        print(f"    Highest: {max(r['high'] for r in records):.2f}")
        print(f"    Lowest:  {min(r['low'] for r in records):.2f}")
        print(f"    Avg Close: {sum(closes) /len(closes):.2f}")

        # Print JSON for parsing
        print(f"\n  # HIST_META##")
        print(json.dumps({
            "code": stock_code,
            "name": stock_name,
            "days": len(records),
            "data": records
        }, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Failed to get history: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stock_hist.py <stock_code> [days]")
        print("Example: python stock_hist.py 600519 30")
        sys.exit(1)

    stock_code = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    days = min(days, 365)  # Limit to 1 year

    get_history(stock_code, days)
