#!/usr/bin/env python3
"""
Search stocks via Yahoo Finance.

Note: yfinance doesn't have a built-in search API.
This script uses Yahoo Finance search API directly.

Usage:
    python yf_search.py <keyword>

Example:
    python yf_search.py apple
    python yf_search.py tesla
"""

import sys
import json
import requests

def search_stocks_yf(keyword):
    try:
        # Yahoo Finance search API
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            'q': keyword,
            'quotesCount': 20,
            'newsCount': 0,
            'listsCount': 0,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        quotes = data.get('quotes', [])
        
        if not quotes:
            print(f"[INFO] No results for '{keyword}'")
            sys.exit(0)
        
        print(f"\n🔍 Yahoo Finance search results for '{keyword}':")
        print(f"{'='*80}")
        print(f"  {'No.':<4} {'Ticker':<12} {'Name':<30} {'Exchange':<15} {'Type':<10}")
        print(f"  {'-'*80}")
        
        results = []
        for idx, quote in enumerate(quotes[:20], 1):
            ticker = quote.get('symbol', 'N/A')
            name = quote.get('shortname', quote.get('longname', 'Unknown'))
            exchange = quote.get('exchange', 'N/A')
            quote_type = quote.get('quoteType', 'N/A')
            
            # Truncate long names
            name_display = name[:28] + '..' if len(name) > 30 else name
            
            print(f"  {idx:<4} {ticker:<12} {name_display:<30} {exchange:<15} {quote_type:<10}")
            
            results.append({
                "index": idx,
                "ticker": ticker,
                "name": name,
                "exchange": exchange,
                "type": quote_type,
                "sector": quote.get('sector', 'N/A'),
                "industry": quote.get('industry', 'N/A')
            })
        
        # Print JSON for parsing
        print(f"\n##SEARCH_META##")
        print(json.dumps({
            "keyword": keyword,
            "total": len(quotes),
            "results": results
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to search: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yf_search.py <keyword>")
        print("Example: python yf_search.py apple")
        sys.exit(1)
    
    keyword = sys.argv[1]
    search_stocks_yf(keyword)
