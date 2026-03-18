#!/usr/bin/env python3
"""
Compare multiple stocks performance.

Usage:
    python yf_compare.py <ticker1> <ticker2> [ticker3...]

Example:
    python yf_compare.py AAPL MSFT GOOGL
    python yf_compare.py 0700.HK 9988.HK 3690.HK
"""

import sys
import json
from datetime import datetime, timedelta

def compare_stocks(tickers):
    try:
        import yfinance as yf
    except ImportError:
        print("[ERROR] yfinance not installed. Run: pip install yfinance")
        sys.exit(1)
    
    results = []
    
    print(f"\n📊 Stock Comparison: {', '.join(tickers)}")
    print(f"{'='*90}")
    print(f"  {'Ticker':<12} {'Name':<20} {'Price':>10} {'1D%':>8} {'1W%':>8} {'1M%':>8} {'YTD%':>8}")
    print(f"  {'-'*90}")
    
    end_date = datetime.now()
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            name = info.get('shortName', ticker)[:18]
            price = info.get('regularMarketPrice', 0)
            
            # Get historical data for different periods
            hist_1d = stock.history(period='2d')
            hist_1w = stock.history(period='5d')
            hist_1m = stock.history(period='1mo')
            hist_ytd = stock.history(start=f"{end_date.year}-01-01")
            
            # Calculate returns
            if len(hist_1d) >= 2:
                ret_1d = (hist_1d['Close'].iloc[-1] / hist_1d['Close'].iloc[-2] - 1) * 100
            else:
                ret_1d = info.get('regularMarketChangePercent', 0)
            
            ret_1w = (hist_1w['Close'].iloc[-1] / hist_1w['Close'].iloc[0] - 1) * 100 if len(hist_1w) > 0 else 0
            ret_1m = (hist_1m['Close'].iloc[-1] / hist_1m['Close'].iloc[0] - 1) * 100 if len(hist_1m) > 0 else 0
            ret_ytd = (hist_ytd['Close'].iloc[-1] / hist_ytd['Close'].iloc[0] - 1) * 100 if len(hist_ytd) > 0 else 0
            
            emoji = "📈" if ret_1d >= 0 else "📉"
            
            print(f"  {ticker:<12} {name:<20} {price:>10.2f} {emoji}{ret_1d:>6.2f}% {ret_1w:>7.2f}% {ret_1m:>7.2f}% {ret_ytd:>7.2f}%")
            
            results.append({
                'ticker': ticker,
                'name': info.get('shortName', ticker),
                'price': price,
                'return_1d': round(ret_1d, 2),
                'return_1w': round(ret_1w, 2),
                'return_1m': round(ret_1m, 2),
                'return_ytd': round(ret_ytd, 2)
            })
            
        except Exception as e:
            print(f"  {ticker:<12} {'Error':<20} {'N/A':>10} {'N/A':>8} {'N/A':>8} {'N/A':>8} {'N/A':>8}")
            results.append({'ticker': ticker, 'error': str(e)})
    
    # Print summary
    if results:
        print(f"\n  Summary:")
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            best_1d = max(valid_results, key=lambda x: x['return_1d'])
            worst_1d = min(valid_results, key=lambda x: x['return_1d'])
            print(f"    Best 1D: {best_1d['ticker']} ({best_1d['return_1d']:+.2f}%)")
            print(f"    Worst 1D: {worst_1d['ticker']} ({worst_1d['return_1d']:+.2f}%)")
    
    # Print JSON for parsing
    print(f"\n##COMPARE_META##")
    print(json.dumps(results, ensure_ascii=False, default=str))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python yf_compare.py <ticker1> <ticker2> [ticker3...]")
        print("Example: python yf_compare.py AAPL MSFT GOOGL")
        sys.exit(1)
    
    tickers = [t.upper() for t in sys.argv[1:]]
    compare_stocks(tickers)
