#!/usr/bin/env python3
"""
Search A-share stocks by name (using Tencent Suggest API).

Usage:
    python stock_search_tx.py <keyword>

Example:
    python stock_search_tx.py 茅台
    python stock_search_tx.py 银行
"""

import sys
import json
import requests

def search_stocks_tx(keyword):
    try:
        # Tencent suggest API
        url = "https://smartbox.gtimg.cn/s3/"
        params = {
            'v': '2',
            'q': keyword,
            't': 'all'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        
        # Tencent returns content with unicode escapes
        data = resp.text
        
        # Decode unicode escapes
        data = data.encode('utf-8').decode('unicode_escape')
        
        if not data or 'v_hint="' not in data:
            print(f"[INFO] No results for '{keyword}'")
            sys.exit(0)
        
        # Parse Tencent suggest format
        content = data.split('v_hint="')[1].split('"')[0]
        if not content:
            print(f"[INFO] No results for '{keyword}'")
            sys.exit(0)
        
        # Format: market~code~name~pinyin~type (items separated by ^)
        stocks = []
        items = content.split('^')
        
        print(f"\n🔍 Search results for '{keyword}':")
        print(f"{'='*60}")
        print(f"  {'No.':<4} {'Code':<8} {'Name':<15} {'Type':<10}")
        print(f"  {'-'*60}")
        
        for idx, item in enumerate(items[:20], 1):
            parts = item.split('~')
            if len(parts) >= 3:
                market = parts[0]
                code = parts[1]
                name = parts[2]
                stock_type = parts[4] if len(parts) > 4 else 'GP-A'
                
                # Filter for A-shares only
                if code.isdigit() and len(code) == 6:
                    print(f"  {idx:<4} {code:<8} {name:<15} {stock_type:<10}")
                    stocks.append({
                        "index": idx,
                        "code": code,
                        "name": name,
                        "market": market,
                        "type": stock_type
                    })
        
        # Print JSON for parsing
        print(f"\n##SEARCH_META##")
        print(json.dumps({
            "keyword": keyword,
            "total": len(stocks),
            "results": stocks
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to search: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stock_search_tx.py <keyword>")
        print("Example: python stock_search_tx.py 茅台")
        sys.exit(1)
    
    keyword = sys.argv[1]
    search_stocks_tx(keyword)
