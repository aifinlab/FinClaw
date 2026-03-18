#!/usr/bin/env python3
"""
Get fund data via BaoStock.

Usage:
    python bs_fund.py <code> [start_date] [end_date]

Example:
    python bs_fund.py sh.510300 2024-01-01 2024-03-12
    python bs_fund.py sz.159915

Fund codes:
    sh.510300 - 沪深300ETF
    sh.510050 - 上证50ETF
    sz.159915 - 创业板ETF
"""

import sys
import json
from datetime import datetime

def get_fund(code, start_date=None, end_date=None):
    try:
        import baostock as bs
    except ImportError:
        print("[ERROR] baostock not installed. Run: pip install baostock")
        sys.exit(1)
    
    try:
        lg = bs.login()
        if lg.error_code != '0':
            print(f"[ERROR] Login failed: {lg.error_msg}")
            sys.exit(1)
        
        if not start_date:
            start_date = '2024-01-01'
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n💰 Fund Data - {code}")
        print(f"Period: {start_date} to {end_date}\n")
        print(f"{'='*90}")
        
        rs = bs.query_history_k_data_plus(
            code,
            "date,code,open,high,low,close,preclose,volume,amount,pctChg",
            start_date=start_date,
            end_date=end_date,
            frequency="d"
        )
        
        if rs.error_code != '0':
            print(f"[ERROR] Query failed: {rs.error_msg}")
            bs.logout()
            sys.exit(1)
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            row = {
                'date': rs.get_row_data()[0],
                'code': rs.get_row_data()[1],
                'open': float(rs.get_row_data()[2]),
                'high': float(rs.get_row_data()[3]),
                'low': float(rs.get_row_data()[4]),
                'close': float(rs.get_row_data()[5]),
                'volume': int(rs.get_row_data()[7]),
                'amount': float(rs.get_row_data()[8]),
                'pct_chg': float(rs.get_row_data()[9]) if rs.get_row_data()[9] else 0
            }
            data_list.append(row)
        
        bs.logout()
        
        if not data_list:
            print(f"[INFO] No data found for {code}")
            sys.exit(0)
        
        print(f"  {'Date':<12} {'Open':>10} {'Close':>10} {'Change%':>10} {'Volume':>15}")
        print(f"  {'-'*90}")
        
        for row in data_list[-10:]:
            change_emoji = "📈" if row['pct_chg'] >= 0 else "📉"
            print(f"  {row['date']:<12} {row['open']:>10.3f} {row['close']:>10.3f} {change_emoji}{row['pct_chg']:>8.2f}% {row['volume']:>15,}")
        
        closes = [r['close'] for r in data_list]
        print(f"\n  Statistics ({len(data_list)} days):")
        print(f"    Return: {((closes[-1] - closes[0]) / closes[0] * 100):.2f}%")
        
        print(f"\n##FUND_META##")
        print(json.dumps({
            'code': code,
            'count': len(data_list),
            'latest_nav': closes[-1]
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bs_fund.py <code> [start_date] [end_date]")
        print("Example: python bs_fund.py sh.510300 2024-01-01 2024-03-12")
        print("\nPopular ETFs:")
        print("  sh.510300 - 沪深300ETF")
        print("  sh.510050 - 上证50ETF")
        print("  sz.159915 - 创业板ETF")
        sys.exit(1)
    
    code = sys.argv[1]
    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None
    
    get_fund(code, start_date, end_date)
