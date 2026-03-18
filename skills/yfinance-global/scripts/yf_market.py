#!/usr/bin/env python3
"""
Get market overview for major indices (S&P 500, Nasdaq, Dow, etc.).

Usage:
    python yf_market.py

Example:
    python yf_market.py
"""

import sys
import json

def get_market_overview():
    try:
        import yfinance as yf
    except ImportError:
        print("[ERROR] yfinance not installed. Run: pip install yfinance")
        sys.exit(1)
    
    # Major indices to track
    indices = {
        '^GSPC': 'S&P 500',
        '^IXIC': 'Nasdaq',
        '^DJI': 'Dow Jones',
        '^RUT': 'Russell 2000',
        '^VIX': 'VIX (Fear Index)',
        '000001.SS': '上证指数',
        '399001.SZ': '深证成指',
        '^HSI': '恒生指数',
        '^N225': '日经225',
        '^FTSE': '英国富时100',
        '^GDAXI': '德国DAX',
    }
    
    results = []
    
    print("\n🌍 Global Market Overview")
    print(f"{'='*70}")
    print(f"  {'Index':<20} {'Price':>12} {'Change':>10} {'Change%':>10}")
    print(f"  {'-'*70}")
    
    for ticker, name in indices.items():
        try:
            idx = yf.Ticker(ticker)
            info = idx.info
            
            price = info.get('regularMarketPrice', 0)
            change = info.get('regularMarketChange', 0)
            change_pct = info.get('regularMarketChangePercent', 0)
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            print(f"  {name:<20} {price:>12.2f} {change:>+10.2f} {change_emoji}{change_pct:>8.2f}%")
            
            results.append({
                'ticker': ticker,
                'name': name,
                'price': price,
                'change': change,
                'change_pct': change_pct
            })
        except Exception as e:
            print(f"  {name:<20} {'N/A':>12} {'N/A':>10} {'N/A':>10}")
            results.append({
                'ticker': ticker,
                'name': name,
                'price': None,
                'change': None,
                'change_pct': None,
                'error': str(e)
            })
    
    # Print JSON for parsing
    print(f"\n##MARKET_META##")
    print(json.dumps(results, ensure_ascii=False, default=str))

if __name__ == "__main__":
    get_market_overview()
