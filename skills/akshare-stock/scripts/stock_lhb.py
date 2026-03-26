#!/usr/bin/env python3
"""
Get daily Dragon Tiger List (龙虎榜) - top traded stocks with unusual activity.

Usage:
    python stock_lhb.py [date]

Example:
    python stock_lhb.py  # Today's data
    python stock_lhb.py 20250311  # Specific date (YYYYMMDD)

The Dragon Tiger List shows:
    - Stocks with abnormal price movement
    - Top buyer/seller brokerages
    - Institutional trading activity
"""

import sys
from datetime import datetime, timedelta
import akshare as ak
import json


def get_lhb(date_str=None):
    try:
        # Get date
        if date_str:
            date = datetime.strptime(date_str, '%Y%m%d')
        else:
            date = datetime.now()

        date_formatted = date.strftime('%Y%m%d')

        print(f"\n🐲 Dragon Tiger List ({date_formatted})")
        print(f"{'=' *90}")

        # Get LHB data
        df = ak.stock_lhb_detail_daily_sina(
    start_date=date_formatted, end_date=date_formatted)

        if df.empty:
            print(f"[INFO] No Dragon Tiger data for {date_formatted}")
            print(f"[INFO] Note: Data may not be available for weekends/holidays")
            sys.exit(0)

        print(
    f"  {
        'No.':<4} {
            'Code':<8} {
                'Name':<15} {
                    'Reason':<30} {
                        'Amount(万)':<12}")
        print(f"  {'-' *90}")

        results = []
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            code = row.get('代码', '')
            name = row.get('名称', '')
            reason = row.get('异动原因', '')[:28]
            amount = row.get('成交额', 0)

            print(f"  {idx:<4} {code:<8} {name:<15} {reason:<30} {amount /10000:>10.2f}")
            results.append({
                'index': idx,
                'code': code,
                'name': name,
                'reason': row.get('异动原因', ''),
                'amount': amount
            })

        print(f"\n  Total: {len(results)} stocks on Dragon Tiger List")

        # Print JSON for parsing
        print(f"\n  # LHB_META##")
        print(json.dumps({
            'date': date_formatted,
            'count': len(results),
            'data': results
        }, ensure_ascii=False, default=str))

    except Exception as e:
        print(f"[ERROR] Failed to get Dragon Tiger list: {e}")
        print(f"[INFO] Try: python stock_lhb.py 20250311")
        sys.exit(1)

if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    get_lhb(date_str)
