#!/usr/bin/env python3
"""
Get top shareholders data via Tushare Pro.

Usage:
    python ts_holders.py <ts_code> [quarter]

Example:
    python ts_holders.py 600519.SH 20231231
    python ts_holders.py 000001.SZ

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

import sys
import os
import json

def get_holders(ts_code, quarter=None):
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
        
        # Query top holders
        if quarter:
            df = pro.top10_holders(ts_code=ts_code, period=quarter)
        else:
            # Get latest
            df = pro.top10_holders(ts_code=ts_code)
        
        if df.empty:
            print(f"[INFO] No holder data for {ts_code}")
            sys.exit(0)
        
        # Get the latest period
        latest_period = df['end_date'].iloc[0] if 'end_date' in df.columns else 'N/A'
        
        print(f"\n👥 Top 10 Shareholders - {ts_code}")
        print(f"Report Period: {latest_period}")
        print(f"{'='*80}")
        print(f"  {'No.':<4} {'Holder Name':<40} {'Shares(万)':>15} {'Ratio':>10}")
        print(f"  {'-'*80}")
        
        results = []
        for idx, row in df.iterrows():
            holder_name = row.get('holder_name', 'N/A')
            hold_amount = row.get('hold_amount', 0) / 10000  # Convert to 万股
            hold_ratio = row.get('hold_ratio', 0)
            
            print(f"  {idx+1:<4} {holder_name:<40} {hold_amount:>15.2f} {hold_ratio:>9.2f}%")
            
            results.append({
                'rank': idx + 1,
                'holder_name': holder_name,
                'hold_amount': round(hold_amount, 2),
                'hold_ratio': hold_ratio
            })
        
        # Calculate total
        total_ratio = sum(r['hold_ratio'] for r in results)
        print(f"  {'-'*80}")
        print(f"  {'Total':<45} {total_ratio:>24.2f}%")
        
        print(f"\n  📊 Analysis:")
        print(f"  {'-'*60}")
        if total_ratio > 50:
            print(f"  ✅ 股权集中，前10大股东持股 {total_ratio:.2f}%")
        else:
            print(f"  ℹ️ 股权分散，前10大股东持股 {total_ratio:.2f}%")
        
        # Print JSON for parsing
        print(f"\n##HOLDERS_META##")
        print(json.dumps({
            'ts_code': ts_code,
            'period': latest_period,
            'count': len(results),
            'total_ratio': round(total_ratio, 2),
            'holders': results
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts_holders.py <ts_code> [quarter]")
        print("Example: python ts_holders.py 600519.SH 20231231")
        sys.exit(1)
    
    ts_code = sys.argv[1]
    quarter = sys.argv[2] if len(sys.argv) > 2 else None
    
    get_holders(ts_code, quarter)
