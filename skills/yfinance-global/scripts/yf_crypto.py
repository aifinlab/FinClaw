#!/usr/bin/env python3
"""
Get cryptocurrency data via Yahoo Finance.

Usage:
    python yf_crypto.py <symbol>

Example:
    python yf_crypto.py BTC-USD
    python yf_crypto.py ETH-USD
    python yf_crypto.py SOL-USD

Popular symbols:
    - BTC-USD (Bitcoin)
    - ETH-USD (Ethereum)
    - SOL-USD (Solana)
    - ADA-USD (Cardano)
    - DOGE-USD (Dogecoin)
"""

import sys
import json

def get_crypto_quote(symbol):
    try:
        import yfinance as yf
    except ImportError:
        print("[ERROR] yfinance not installed. Run: pip install yfinance")
        sys.exit(1)
    
    try:
        # Ensure symbol ends with -USD
        if not symbol.endswith('-USD') and not symbol.endswith('-USDT'):
            symbol = f"{symbol}-USD"
        
        crypto = yf.Ticker(symbol)
        info = crypto.info
        
        if not info or 'regularMarketPrice' not in info:
            print(f"[ERROR] No data for {symbol}")
            sys.exit(1)
        
        # Get historical data for 24h change
        hist = crypto.history(period='2d')
        
        result = {
            'symbol': symbol,
            'name': info.get('name', symbol),
            'price': info.get('regularMarketPrice', 0),
            'change_24h': info.get('regularMarketChange', 0),
            'change_24h_pct': info.get('regularMarketChangePercent', 0),
            'market_cap': info.get('marketCap', 0),
            'volume_24h': info.get('regularMarketVolume', 0),
            'circulating_supply': info.get('circulatingSupply', 0),
            'high_24h': info.get('regularMarketDayHigh', 0),
            'low_24h': info.get('regularMarketDayLow', 0),
        }
        
        # Calculate additional metrics
        if len(hist) >= 2:
            result['previous_close'] = hist['Close'].iloc[-2]
        else:
            result['previous_close'] = result['price'] - result['change_24h']
        
        # Print readable format
        change_emoji = "🚀" if result['change_24h_pct'] >= 5 else ("📈" if result['change_24h_pct'] >= 0 else "📉")
        
        print(f"\n₿ {result['name']} ({symbol})")
        print(f"{'='*60}")
        print(f"  Price: ${result['price']:,.2f}")
        print(f"  24h Change: {change_emoji} {result['change_24h']:+.2f} ({result['change_24h_pct']:+.2f}%)")
        print(f"  24h High: ${result['high_24h']:,.2f}")
        print(f"  24h Low: ${result['low_24h']:,.2f}")
        print(f"  24h Volume: {result['volume_24h']:,.0f}")
        
        if result['market_cap']:
            print(f"  Market Cap: ${result['market_cap']/1e9:.2f}B")
        
        if result['circulating_supply']:
            print(f"  Circulating Supply: {result['circulating_supply']:,.0f}")
        
        # Print JSON for parsing
        print(f"\n##CRYPTO_META##")
        print(json.dumps(result, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get crypto data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yf_crypto.py <symbol>")
        print("Example: python yf_crypto.py BTC-USD")
        print("         python yf_crypto.py ETH-USD")
        print("\nPopular symbols: BTC-USD, ETH-USD, SOL-USD, ADA-USD")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    get_crypto_quote(symbol)
