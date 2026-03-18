#!/usr/bin/env python3
"""
Get historical price data via Yahoo Finance (yfinance).

Usage:
    python yf_hist.py <ticker> [days]

Example:
    python yf_hist.py AAPL 30
    python yf_hist.py 0700.HK 60

Arguments:
    ticker: Stock ticker symbol
    days: Number of days (default: 30, max: 365)
"""

import sys
import json
from datetime import datetime, timedelta

def get_history_yf(ticker, days=30):
    try:
        import yfinance as yf
    except ImportError:
        print("[ERROR] yfinance not installed. Run: pip install yfinance")
        sys.exit(1)
    
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        stock_name = info.get('longName', info.get('shortName', ticker))
        currency = info.get('currency', 'USD')
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"[ERROR] No historical data for {ticker}")
            sys.exit(1)
        
        # Convert to list of dicts
        records = []
        for index, row in df.iterrows():
            records.append({
                "date": index.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume']),
                "dividends": round(row['Dividends'], 4) if 'Dividends' in row else 0,
                "splits": row['Stock Splits'] if 'Stock Splits' in row else 0,
            })
        
        # Print readable format
        print(f"\n📊 {stock_name} ({ticker}) - Historical Data")
        print(f"{'='*70}")
        print(f"  Period: {records[0]['date']} to {records[-1]['date']}")
        print(f"  Total days: {len(records)}")
        print(f"  Currency: {currency}\n")
        
        # Print recent 10 days
        print("  Recent 10 days:")
        print(f"  {'Date':^12} {'Open':>10} {'Close':>10} {'High':>10} {'Low':>10} {'Volume':>12}")
        print(f"  {'-'*70}")
        for r in records[-10:]:
            print(f"  {r['date']:^12} {r['open']:>10.2f} {r['close']:>10.2f} {r['high']:>10.2f} {r['low']:>10.2f} {r['volume']:>12,}")
        
        # Calculate stats
        closes = [r['close'] for r in records]
        print(f"\n  Statistics:")
        print(f"    Highest: {max(r['high'] for r in records):.2f}")
        print(f"    Lowest:  {min(r['low'] for r in records):.2f}")
        print(f"    Avg Close: {sum(closes)/len(closes):.2f}")
        print(f"    Return: {((closes[-1] - closes[0]) / closes[0] * 100):.2f}%")
        
        # Print JSON for parsing
        print(f"\n##HIST_META##")
        print(json.dumps({
            "ticker": ticker,
            "name": stock_name,
            "currency": currency,
            "days": len(records),
            "data": records
        }, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get history: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yf_hist.py <ticker> [days]")
        print("Example: python yf_hist.py AAPL 30")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    days = min(days, 365)  # Limit to 1 year
    
    get_history_yf(ticker, days)
