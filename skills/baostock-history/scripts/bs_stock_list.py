#!/usr/bin/env python3
"""
Get all A-share stock list via BaoStock.

Usage:
    python bs_stock_list.py [market]

Example:
    python bs_stock_list.py
    python bs_stock_list.py sh
    python bs_stock_list.py sz

Arguments:
    market: sh (Shanghai), sz (Shenzhen), or empty for all
"""

import sys
import json

def get_stock_list(market=None):
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
        
        print(f"\n📋 A-Share Stock List")
        print(f"{'='*90}")
        
        rs = bs.query_all_stock(day="")
        
        if rs.error_code != '0':
            print(f"[ERROR] Query failed: {rs.error_msg}")
            bs.logout()
            sys.exit(1)
        
        stocks = []
        while (rs.error_code == '0') & rs.next():
            code = rs.get_row_data()[0]
            name = rs.get_row_data()[1]
            
            # Filter by market if specified
            if market:
                if market == 'sh' and not code.startswith('sh.'):
                    continue
                if market == 'sz' and not code.startswith('sz.'):
                    continue
            
            stocks.append({'code': code, 'name': name})
        
        bs.logout()
        
        print(f"\n  Total stocks: {len(stocks)}\n")
        print(f"  {'No.':<6} {'Code':<15} {'Name':<20}")
        print(f"  {'-'*50}")
        
        # Show first 30
        for idx, stock in enumerate(stocks[:30], 1):
            print(f"  {idx:<6} {stock['code']:<15} {stock['name']:<20}")
        
        if len(stocks) > 30:
            print(f"  ... and {len(stocks) - 30} more")
        
        # Count by market
        sh_count = len([s for s in stocks if s['code'].startswith('sh.')])
        sz_count = len([s for s in stocks if s['code'].startswith('sz.')])
        
        print(f"\n  Market breakdown:")
        print(f"    Shanghai: {sh_count}")
        print(f"    Shenzhen: {sz_count}")
        
        print(f"\n##STOCK_LIST_META##")
        print(json.dumps({
            'total': len(stocks),
            'shanghai': sh_count,
            'shenzhen': sz_count,
            'stocks': stocks[:50]
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    market = sys.argv[1] if len(sys.argv) > 1 else None
    if market and market not in ['sh', 'sz']:
        print("Usage: python bs_stock_list.py [sh|sz]")
        print("Example: python bs_stock_list.py sh")
        sys.exit(1)
    
    get_stock_list(market)
