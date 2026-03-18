#!/usr/bin/env python3
"""
Calculate technical indicators for a stock (RSI, MACD, Moving Averages).

Usage:
    python yf_tech.py <ticker>

Example:
    python yf_tech.py AAPL
    python yf_tech.py 0700.HK
"""

import sys
import json
import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def get_technical_analysis(ticker):
    try:
        import yfinance as yf
    except ImportError:
        print("[ERROR] yfinance not installed. Run: pip install yfinance")
        sys.exit(1)
    
    try:
        # Get historical data
        stock = yf.Ticker(ticker)
        df = stock.history(period='3mo')
        
        if df.empty:
            print(f"[ERROR] No data for {ticker}")
            sys.exit(1)
        
        # Get current price
        info = stock.info
        current_price = df['Close'].iloc[-1]
        
        # Calculate Moving Averages
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        # Calculate RSI
        df['RSI'] = calculate_rsi(df['Close'])
        
        # Calculate MACD
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df['Close'])
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Determine trend
        trend = "Bullish 📈" if latest['Close'] > latest['MA20'] else "Bearish 📉"
        
        # RSI signal
        rsi_value = latest['RSI']
        if rsi_value > 70:
            rsi_signal = "Overbought 🔴"
        elif rsi_value < 30:
            rsi_signal = "Oversold 🟢"
        else:
            rsi_signal = "Neutral ⚪"
        
        # MACD signal
        macd_signal = "Bullish 📈" if latest['MACD'] > latest['MACD_Signal'] else "Bearish 📉"
        
        result = {
            'ticker': ticker,
            'price': round(current_price, 2),
            'trend': trend,
            'ma5': round(latest['MA5'], 2),
            'ma10': round(latest['MA10'], 2),
            'ma20': round(latest['MA20'], 2),
            'ma60': round(latest['MA60'], 2),
            'rsi': round(rsi_value, 2),
            'rsi_signal': rsi_signal,
            'macd': round(latest['MACD'], 4),
            'macd_signal': macd_signal,
            'volume': int(latest['Volume'])
        }
        
        # Print readable format
        print(f"\n📊 Technical Analysis: {ticker}")
        print(f"{'='*60}")
        print(f"  Current Price: {result['price']}")
        print(f"  Trend: {result['trend']}")
        print(f"\n  Moving Averages:")
        print(f"    MA5:  {result['ma5']}")
        print(f"    MA10: {result['ma10']}")
        print(f"    MA20: {result['ma20']}")
        print(f"    MA60: {result['ma60']}")
        print(f"\n  RSI (14): {result['rsi']} - {result['rsi_signal']}")
        print(f"  MACD: {result['macd']:.4f} - {result['macd_signal']}")
        
        # Support/Resistance levels
        recent = df.tail(20)
        support = recent['Low'].min()
        resistance = recent['High'].max()
        print(f"\n  Support: {support:.2f}")
        print(f"  Resistance: {resistance:.2f}")
        
        result['support'] = round(support, 2)
        result['resistance'] = round(resistance, 2)
        
        # Print JSON for parsing
        print(f"\n##TECH_META##")
        print(json.dumps(result, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get technical analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yf_tech.py <ticker>")
        print("Example: python yf_tech.py AAPL")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    get_technical_analysis(ticker)
