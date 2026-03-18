#!/usr/bin/env python3
"""
Get stock quote and info via Yahoo Finance (yfinance).

Usage:
    python yf_quote.py <ticker>

Example:
    python yf_quote.py AAPL
    python yf_quote.py 0700.HK
    python yf_quote.py TSLA

Ticker format:
    - US Stocks: AAPL, TSLA, MSFT
    - HK Stocks: 0700.HK, 9988.HK
    - Indices: ^GSPC (S&P 500)
"""

import sys
import json
from datetime import datetime

def get_quote_yf(ticker):
    try:
        import yfinance as yf
    except ImportError:
        print("[ERROR] yfinance not installed. Run: pip install yfinance")
        sys.exit(1)
    
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or 'regularMarketPrice' not in info:
            print(f"[ERROR] No data for ticker {ticker}")
            sys.exit(1)
        
        # Extract key info
        result = {
            "ticker": ticker,
            "name": info.get('longName', info.get('shortName', 'Unknown')),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "price": info.get('regularMarketPrice', 0),
            "previous_close": info.get('regularMarketPreviousClose', 0),
            "open": info.get('regularMarketOpen', 0),
            "high": info.get('regularMarketDayHigh', 0),
            "low": info.get('regularMarketDayLow', 0),
            "volume": info.get('regularMarketVolume', 0),
            "change": info.get('regularMarketChange', 0),
            "change_pct": info.get('regularMarketChangePercent', 0),
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', info.get('forwardPE', 0)),
            "pb_ratio": info.get('priceToBook', 0),
            "dividend_yield": info.get('dividendYield', 0),
            "52w_high": info.get('fiftyTwoWeekHigh', 0),
            "52w_low": info.get('fiftyTwoWeekLow', 0),
            "avg_volume": info.get('averageVolume', 0),
            "currency": info.get('currency', 'USD'),
        }
        
        # Print readable format
        change_emoji = "📈" if result['change'] >= 0 else "📉"
        currency = result['currency']
        
        print(f"\n🌐 {result['name']} ({ticker})")
        print(f"{'='*60}")
        print(f"  最新价: {result['price']:.2f} {currency}")
        if result['change_pct']:
            print(f"  涨跌幅: {change_emoji} {result['change_pct']:.2f}%")
        if result['change']:
            print(f"  涨跌额: {result['change']:.2f} {currency}")
        print(f"  今开: {result['open']:.2f}")
        print(f"  最高: {result['high']:.2f}")
        print(f"  最低: {result['low']:.2f}")
        print(f"  昨收: {result['previous_close']:.2f}")
        print(f"  成交量: {result['volume']:,}")
        print(f"  平均成交量: {result['avg_volume']:,}")
        print(f"  市值: {result['market_cap']/1e9:.2f}B {currency}" if result['market_cap'] else "  市值: N/A")
        print(f"  市盈率: {result['pe_ratio']:.2f}" if result['pe_ratio'] else "  市盈率: N/A")
        print(f"  市净率: {result['pb_ratio']:.2f}" if result['pb_ratio'] else "  市净率: N/A")
        if result['dividend_yield']:
            print(f"  股息率: {result['dividend_yield']*100:.2f}%")
        print(f"  52周最高: {result['52w_high']:.2f}")
        print(f"  52周最低: {result['52w_low']:.2f}")
        print(f"  行业: {result['industry']}")
        print(f"  板块: {result['sector']}")
        
        # Print JSON for parsing
        print(f"\n##QUOTE_META##")
        print(json.dumps(result, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get quote: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yf_quote.py <ticker>")
        print("Example: python yf_quote.py AAPL")
        print("         python yf_quote.py 0700.HK")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    get_quote_yf(ticker)
