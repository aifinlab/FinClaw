#!/usr/bin/env python3
"""
Get balance sheet data via Tushare Pro.

Usage:
    python ts_balance_sheet.py <ts_code> [year]

Example:
    python ts_balance_sheet.py 600519.SH 2023
    python ts_balance_sheet.py 000001.SZ 2022

Arguments:
    ts_code: Stock code (e.g., 600519.SH)
    year: Report year (default: 2023)

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

import sys
import os
import json

def get_balance_sheet(ts_code, year=2023):
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
        
        # Query balance sheet
        df = pro.balancesheet(ts_code=ts_code, period=f"{year}1231")
        
        if df.empty:
            print(f"[INFO] No balance sheet data for {ts_code} in {year}")
            sys.exit(0)
        
        # Get the latest report
        row = df.iloc[0]
        
        print(f"\n📊 Balance Sheet - {ts_code} ({year})")
        print(f"{'='*80}")
        
        # Key metrics
        result = {
            'ts_code': ts_code,
            'period': row.get('end_date', 'N/A'),
            'total_assets': round(row.get('total_assets', 0) / 1e8, 2),  # 亿元
            'total_liabilities': round(row.get('total_liab', 0) / 1e8, 2),
            'total_equity': round(row.get('total_hldr_eqy_exc_min_int', 0) / 1e8, 2),
            'current_assets': round(row.get('total_cur_assets', 0) / 1e8, 2),
            'current_liabilities': round(row.get('total_cur_liab', 0) / 1e8, 2),
            'inventory': round(row.get('inventories', 0) / 1e8, 2),
            'cash': round(row.get('money_cap', 0) / 1e8, 2),
            'receivables': round(row.get('accounts_receiv', 0) / 1e8, 2),
            'fixed_assets': round(row.get('fix_assets', 0) / 1e8, 2),
        }
        
        # Calculate ratios
        if result['current_liabilities'] > 0:
            result['current_ratio'] = round(result['current_assets'] / result['current_liabilities'], 2)
        else:
            result['current_ratio'] = 0
        
        if result['total_equity'] > 0:
            result['debt_to_equity'] = round(result['total_liabilities'] / result['total_equity'], 2)
        else:
            result['debt_to_equity'] = 0
        
        print(f"\n  📈 资产状况 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  总资产:     {result['total_assets']:>15.2f}")
        print(f"  流动资产:   {result['current_assets']:>15.2f}")
        print(f"  现金:       {result['cash']:>15.2f}")
        print(f"  应收账款:   {result['receivables']:>15.2f}")
        print(f"  存货:       {result['inventory']:>15.2f}")
        print(f"  固定资产:   {result['fixed_assets']:>15.2f}")
        
        print(f"\n  📉 负债状况 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  总负债:     {result['total_liabilities']:>15.2f}")
        print(f"  流动负债:   {result['current_liabilities']:>15.2f}")
        
        print(f"\n  💰 股东权益 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  股东权益:   {result['total_equity']:>15.2f}")
        
        print(f"\n  📊 关键指标")
        print(f"  {'-'*60}")
        print(f"  流动比率:   {result['current_ratio']:>15.2f}")
        print(f"  产权比率:   {result['debt_to_equity']:>15.2f}")
        
        # Print JSON for parsing
        print(f"\n##BALANCE_META##")
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts_balance_sheet.py <ts_code> [year]")
        print("Example: python ts_balance_sheet.py 600519.SH 2023")
        sys.exit(1)
    
    ts_code = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2023
    
    get_balance_sheet(ts_code, year)
