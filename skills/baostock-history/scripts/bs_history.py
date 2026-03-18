#!/usr/bin/env python3
"""
Get historical K-line data via BaoStock.

Usage:
    python bs_history.py <code> [start_date] [end_date] [adjust]

Example:
    python bs_history.py sh.600519 2020-01-01 2024-03-12 2
    python bs_history.py sz.000001

Arguments:
    code: Stock code (e.g., sh.600519, sz.000001)
    start_date: Start date (YYYY-MM-DD, default: 2020-01-01)
    end_date: End date (YYYY-MM-DD, default: today)
    adjust: Price adjustment (1=none, 2=forward, 3=backward, default: 2)

Adjust types:
    1 = No adjustment (original prices)
    2 = Forward adjusted (recommended for backtesting)
    3 = Backward adjusted
"""

import sys
import json
from datetime import datetime, timedelta

def get_history(code, start_date=None, end_date=None, adjust='2'):
    try:
        import baostock as bs
    except ImportError:
        print("[ERROR] baostock not installed. Run: pip install baostock")
        sys.exit(1)
    
    try:
        # Login to BaoStock
        lg = bs.login()
        if lg.error_code != '0':
            print(f"[ERROR] Login failed: {lg.error_msg}")
            sys.exit(1)
        
        # Set default dates
        if not start_date:
            start_date = '2020-01-01'
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Map adjust parameter
        adjust_map = {'1': '1', '2': '2', '3': '3'}
        adjust_type = adjust_map.get(adjust, '2')
        adjust_name = {'1': 'No Adjust', '2': 'Forward Adjust', '3': 'Backward Adjust'}.get(adjust_type, 'Forward Adjust')
        
        print(f"\n📈 Historical Data - {code}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Adjustment: {adjust_name}\n")
        print(f"{'='*90}")
        
        # Query history K-line
        rs = bs.query_history_k_data_plus(
            code,
            "date,code,open,high,low,close,preclose,volume,amount,turn,pctChg",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag=adjust_type
        )
        
        if rs.error_code != '0':
            print(f"[ERROR] Query failed: {rs.error_msg}")
            bs.logout()
            sys.exit(1)
        
        # Parse data
        data_list = []
        while (rs.error_code == '0') & rs.next():
            row = {
                'date': rs.get_row_data()[0],
                'code': rs.get_row_data()[1],
                'open': float(rs.get_row_data()[2]),
                'high': float(rs.get_row_data()[3]),
                'low': float(rs.get_row_data()[4]),
                'close': float(rs.get_row_data()[5]),
                'preclose': float(rs.get_row_data()[6]),
                'volume': int(rs.get_row_data()[7]),
                'amount': float(rs.get_row_data()[8]),
                'turnover': float(rs.get_row_data()[9]) if rs.get_row_data()[9] else 0,
                'pct_chg': float(rs.get_row_data()[10]) if rs.get_row_data()[10] else 0
            }
            data_list.append(row)
        
        bs.logout()
        
        if not data_list:
            print(f"[INFO] No data found for {code}")
            sys.exit(0)
        
        # Display data
        print(f"  {'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Change%':>10} {'Volume':>15}")
        print(f"  {'-'*90}")
        
        # Show last 15 days
        for row in data_list[-15:]:
            change_emoji = "📈" if row['pct_chg'] >= 0 else "📉"
            print(f"  {row['date']:<12} {row['open']:>10.2f} {row['high']:>10.2f} {row['low']:>10.2f} {row['close']:>10.2f} {change_emoji}{row['pct_chg']:>8.2f}% {row['volume']:>15,}")
        
        # Statistics
        closes = [r['close'] for r in data_list]
        print(f"\n  {'='*90}")
        print(f"  Statistics ({len(data_list)} trading days):")
        print(f"    Highest: {max(r['high'] for r in data_list):.2f}")
        print(f"    Lowest:  {min(r['low'] for r in data_list):.2f}")
        print(f"    Avg Close: {sum(closes)/len(closes):.2f}")
        print(f"    Total Return: {((closes[-1] - closes[0]) / closes[0] * 100):.2f}%")
        
        # Print JSON for parsing
        print(f"\n##HISTORY_META##")
        print(json.dumps({
            'code': code,
            'period': f"{start_date} to {end_date}",
            'adjust': adjust_name,
            'count': len(data_list),
            'data': data_list
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bs_history.py <code> [start_date] [end_date] [adjust]")
        print("Example: python bs_history.py sh.600519 2020-01-01 2024-03-12 2")
        print("\nAdjust types:")
        print("  1 = No adjustment")
        print("  2 = Forward adjusted (recommended)")
        print("  3 = Backward adjusted")
        sys.exit(1)
    
    code = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None
    adjust = sys.argv[4] if len(sys.argv) > 4 else '2'
    
    get_history(code, start_date, end_date, adjust)
