#!/usr/bin/env python3
"""
Get income statement data via Tushare Pro.

Usage:
    python ts_income.py <ts_code> [year]

Example:
    python ts_income.py 600519.SH 2023
    python ts_income.py 000001.SZ 2022

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

import sys
import os
import json

def get_income(ts_code, year=2023):
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
        
        # Query income statement
        df = pro.income(ts_code=ts_code, period=f"{year}1231")
        
        if df.empty:
            print(f"[INFO] No income data for {ts_code} in {year}")
            sys.exit(0)
        
        row = df.iloc[0]
        
        print(f"\n📈 Income Statement - {ts_code} ({year})")
        print(f"{'='*80}")
        
        result = {
            'ts_code': ts_code,
            'period': row.get('end_date', 'N/A'),
            'revenue': round(row.get('total_revenue', 0) / 1e8, 2),  # 亿元
            'operating_cost': round(row.get('oper_cost', 0) / 1e8, 2),
            'gross_profit': 0,
            'operating_expenses': round(row.get('operate_exp', 0) / 1e8, 2),
            'operating_income': round(row.get('operate_profit', 0) / 1e8, 2),
            'net_income': round(row.get('n_income_attr_p', 0) / 1e8, 2),
            'rd_expenses': round(row.get('rd_exp', 0) / 1e8, 2),
            'basic_eps': row.get('basic_eps', 0),
            'diluted_eps': row.get('diluted_eps', 0),
        }
        
        # Calculate gross profit
        result['gross_profit'] = round(result['revenue'] - result['operating_cost'], 2)
        
        # Calculate margins
        if result['revenue'] > 0:
            result['gross_margin'] = round(result['gross_profit'] / result['revenue'] * 100, 2)
            result['operating_margin'] = round(result['operating_income'] / result['revenue'] * 100, 2)
            result['net_margin'] = round(result['net_income'] / result['revenue'] * 100, 2)
        else:
            result['gross_margin'] = 0
            result['operating_margin'] = 0
            result['net_margin'] = 0
        
        print(f"\n  💰 营业收入 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  营业总收入: {result['revenue']:>15.2f}")
        print(f"  营业成本:   {result['operating_cost']:>15.2f}")
        print(f"  毛利:       {result['gross_profit']:>15.2f}")
        
        print(f"\n  💸 费用支出 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  营业费用:   {result['operating_expenses']:>15.2f}")
        print(f"  研发费用:   {result['rd_expenses']:>15.2f}")
        
        print(f"\n  📊 盈利能力 (单位: 亿元)")
        print(f"  {'-'*60}")
        print(f"  营业利润:   {result['operating_income']:>15.2f}")
        print(f"  净利润:     {result['net_income']:>15.2f}")
        
        print(f"\n  📈 利润率")
        print(f"  {'-'*60}")
        print(f"  毛利率:     {result['gross_margin']:>15.2f}%")
        print(f"  营业利润率: {result['operating_margin']:>15.2f}%")
        print(f"  净利率:     {result['net_margin']:>15.2f}%")
        
        print(f"\n  💵 每股收益")
        print(f"  {'-'*60}")
        print(f"  基本EPS:    {result['basic_eps']:>15.2f}")
        print(f"  稀释EPS:    {result['diluted_eps']:>15.2f}")
        
        # Print JSON for parsing
        print(f"\n##INCOME_META##")
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts_income.py <ts_code> [year]")
        print("Example: python ts_income.py 600519.SH 2023")
        sys.exit(1)
    
    ts_code = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2023
    
    get_income(ts_code, year)
