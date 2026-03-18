#!/usr/bin/env python3
"""
Get cash flow statement via Tushare Pro.

Usage:
    python ts_cashflow.py <ts_code> [year]

Example:
    python ts_cashflow.py 600519.SH 2023

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

import sys
import os
import json

def get_cashflow(ts_code, year=2023):
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
        
        # Query cash flow
        df = pro.cashflow(ts_code=ts_code, period=f"{year}1231")
        
        if df.empty:
            print(f"[INFO] No cash flow data for {ts_code} in {year}")
            sys.exit(0)
        
        row = df.iloc[0]
        
        print(f"\n💵 Cash Flow Statement - {ts_code} ({year})")
        print(f"{'='*80}")
        
        result = {
            'ts_code': ts_code,
            'period': row.get('end_date', 'N/A'),
            'operating_cf': round(row.get('n_cashflow_act', 0) / 1e8, 2),  # 亿元
            'investing_cf': round(row.get('n_cashflow_inv_act', 0) / 1e8, 2),
            'financing_cf': round(row.get('n_cashflow_fnc_act', 0) / 1e8, 2),
            'net_increase': round(row.get('c_recp_return invest', 0) / 1e8, 2),
            'cash_begin': round(row.get('cash_cash_equ_beg_period', 0) / 1e8, 2),
            'cash_end': round(row.get('c_end_bal_cash', 0) / 1e8, 2),
        }
        
        print(f"\n  🔄 经营活动现金流 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  经营现金流净额: {result['operating_cf']:>12.2f}")
        
        print(f"\n  💰 投资活动现金流 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  投资现金流净额: {result['investing_cf']:>12.2f}")
        
        print(f"\n  💳 筹资活动现金流 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  筹资现金流净额: {result['financing_cf']:>12.2f}")
        
        print(f"\n  📊 现金状况 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  期初现金:       {result['cash_begin']:>12.2f}")
        print(f"  期末现金:       {result['cash_end']:>12.2f}")
        
        # Analysis
        print(f"\n  📈 现金流分析")
        print(f"  {'-'*60}")
        if result['operating_cf'] > 0:
            print(f"  ✅ 经营现金流为正，主营业务健康")
        else:
            print(f"  ⚠️  经营现金流为负，需关注主营业务")
        
        if result['investing_cf'] < 0:
            print(f"  ✅ 投资现金流为负，可能在扩张投资")
        else:
            print(f"  ℹ️  投资现金流为正，可能在处置资产")
        
        if result['financing_cf'] > 0:
            print(f"  ℹ️  筹资现金流为正，有融资活动")
        else:
            print(f"  ✅ 筹资现金流为负，可能在还债或分红")
        
        # Print JSON for parsing
        print(f"\n##CASHFLOW_META##")
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts_cashflow.py <ts_code> [year]")
        print("Example: python ts_cashflow.py 600519.SH 2023")
        sys.exit(1)
    
    ts_code = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2023
    
    get_cashflow(ts_code, year)
