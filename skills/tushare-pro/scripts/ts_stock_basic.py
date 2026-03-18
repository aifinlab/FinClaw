#!/usr/bin/env python3
"""
Get stock basic information via Tushare Pro.

Usage:
    python ts_stock_basic.py [ts_code]

Example:
    python ts_stock_basic.py 000001.SZ
    python ts_stock_basic.py 600519.SH

Environment:
    TUSHARE_TOKEN - Your Tushare API token
"""

import sys
import os
import json

def get_stock_basic(ts_code=None):
    try:
        import tushare as ts
    except ImportError:
        print("[ERROR] tushare not installed. Run: pip install tushare")
        sys.exit(1)
    
    # Get token from environment
    token = os.environ.get('TUSHARE_TOKEN')
    if not token:
        print("[ERROR] TUSHARE_TOKEN not set")
        print("Please set your Tushare token: export TUSHARE_TOKEN='your-token'")
        sys.exit(1)
    
    try:
        # Initialize Tushare Pro
        pro = ts.pro_api(token)
        
        if ts_code:
            # Query specific stock
            df = pro.stock_basic(ts_code=ts_code)
        else:
            # Query all stocks (limit to first 20)
            df = pro.stock_basic()
            df = df.head(20)
        
        if df.empty:
            print(f"[INFO] No data found for {ts_code}")
            sys.exit(0)
        
        print(f"\n📊 Stock Basic Information")
        print(f"{'='*80}")
        
        results = []
        for _, row in df.iterrows():
            result = {
                'ts_code': row.get('ts_code', 'N/A'),
                'symbol': row.get('symbol', 'N/A'),
                'name': row.get('name', 'N/A'),
                'area': row.get('area', 'N/A'),
                'industry': row.get('industry', 'N/A'),
                'market': row.get('market', 'N/A'),
                'list_date': row.get('list_date', 'N/A'),
                'is_hs': row.get('is_hs', 'N')
            }
            
            print(f"\n  代码: {result['ts_code']}")
            print(f"  名称: {result['name']}")
            print(f"  地区: {result['area']}")
            print(f"  行业: {result['industry']}")
            print(f"  市场: {result['market']}")
            print(f"  上市日期: {result['list_date']}")
            print(f"  沪深港通: {'是' if result['is_hs'] == 'Y' else '否'}")
            print(f"  {'-'*60}")
            
            results.append(result)
        
        # Print JSON for parsing
        print(f"\n##BASIC_META##")
        print(json.dumps(results, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ts_code = sys.argv[1] if len(sys.argv) > 1 else None
    get_stock_basic(ts_code)
