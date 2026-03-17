#!/usr/bin/env python3
"""
Search A-share stocks by name or code.

Usage:
    python stock_search.py <keyword>

Example:
    python stock_search.py 茅台
    python stock_search.py 银行
"""

import sys
import json

def search_stocks(keyword):
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] akshare not installed. Run: pip install akshare")
        sys.exit(1)
    
    try:
        # Get all stocks
        df = ak.stock_zh_a_spot_em()
        
        # Search by name or code
        keyword = keyword.strip()
        
        if keyword.isdigit():
            # Search by code (partial match)
            matches = df[df['代码'].str.contains(keyword)]
        else:
            # Search by name
            matches = df[df['名称'].str.contains(keyword, na=False)]
        
        if matches.empty:
            print(f"[INFO] No stocks found for '{keyword}'")
            sys.exit(0)
        
        # Get top 20 results
        results = []
        print(f"\n🔍 Search results for '{keyword}':")
        print(f"{'='*60}")
        print(f"  {'No.':<4} {'Code':<8} {'Name':<12} {'Price':<10} {'Change%':<10}")
        print(f"  {'-'*60}")
        
        for idx, (_, row) in enumerate(matches.head(20).iterrows(), 1):
            code = row['代码']
            name = row['名称']
            price = row['最新价'] if pd.notna(row['最新价']) else '-'
            change = row['涨跌幅'] if pd.notna(row['涨跌幅']) else '-'
            
            change_str = f"{change:.2f}%" if isinstance(change, (int, float)) else str(change)
            price_str = f"{price:.2f}" if isinstance(price, (int, float)) else str(price)
            
            print(f"  {idx:<4} {code:<8} {name:<12} {price_str:<10} {change_str:<10}")
            
            results.append({
                "index": idx,
                "code": code,
                "name": name,
                "price": price,
                "change_pct": change
            })
        
        if len(matches) > 20:
            print(f"\n  ... and {len(matches) - 20} more results")
        
        # Print JSON for parsing
        print(f"\n##SEARCH_META##")
        print(json.dumps({
            "keyword": keyword,
            "total": len(matches),
            "results": results
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to search: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import pandas as pd
    
    if len(sys.argv) < 2:
        print("Usage: python stock_search.py <keyword>")
        print("Example: python stock_search.py 茅台")
        sys.exit(1)
    
    keyword = sys.argv[1]
    search_stocks(keyword)
