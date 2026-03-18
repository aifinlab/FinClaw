#!/usr/bin/env python3
"""
Get technical indicators via 智兔数服 (Zhitu API).

Usage:
    python zhitu_tech.py <code> <indicator> [days]

Example:
    python zhitu_tech.py 000001 MACD
    python zhitu_tech.py 600519 KDJ 30
    python zhitu_tech.py 000001 BOLL

Indicators:
    MACD - Moving Average Convergence Divergence
    KDJ  - Stochastic Oscillator
    BOLL - Bollinger Bands
    MA   - Moving Average

Arguments:
    code: Stock code
    indicator: Technical indicator type
    days: Number of days (default: 30)
"""

import sys
import json
import requests

API_BASE = "https://api.zhituapi.com"
TOKEN = "ZHITU_TOKEN_LIMIT_TEST"

def get_tech_indicator(code, indicator, days=30):
    # Normalize code
    code = code.upper()
    if '.' not in code:
        if code.startswith('6') or code.startswith('688'):
            code = code + '.SH'
        elif code.startswith('0') or code.startswith('3'):
            code = code + '.SZ'
        elif code.startswith('4') or code.startswith('8'):
            code = code + '.BJ'
    
    indicator = indicator.upper()
    valid_indicators = ['MACD', 'KDJ', 'BOLL', 'MA']
    
    if indicator not in valid_indicators:
        print(f"[ERROR] Invalid indicator. Choose from: {', '.join(valid_indicators)}")
        sys.exit(1)
    
    try:
        url = f"{API_BASE}/hs/history/{indicator.lower()}/{code}/d/n?token={TOKEN}"
        
        print(f"\n📈 Technical Indicator - {code}")
        print(f"Indicator: {indicator}\n")
        print(f"{'='*80}")
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if not isinstance(data, list) or len(data) == 0:
            print(f"[INFO] No data found for {code}")
            sys.exit(0)
        
        # Take last N days
        data = data[-days:]
        
        # Display based on indicator type
        if indicator == 'MACD':
            print(f"  {'Date':<12} {'DIF':>10} {'DEA':>10} {'MACD':>10}")
            print(f"  {'-'*50}")
            for item in data:
                print(f"  {item.get('d', 'N/A'):<12} {float(item.get('dif', 0)):>10.4f} {float(item.get('dea', 0)):>10.4f} {float(item.get('macd', 0)):>10.4f}")
        
        elif indicator == 'KDJ':
            print(f"  {'Date':<12} {'K':>8} {'D':>8} {'J':>8}")
            print(f"  {'-'*40}")
            for item in data:
                print(f"  {item.get('d', 'N/A'):<12} {float(item.get('k', 0)):>8.2f} {float(item.get('d', 0)):>8.2f} {float(item.get('j', 0)):>8.2f}")
        
        elif indicator == 'BOLL':
            print(f"  {'Date':<12} {'UP':>10} {'MID':>10} {'LOW':>10}")
            print(f"  {'-'*50}")
            for item in data:
                print(f"  {item.get('d', 'N/A'):<12} {float(item.get('up', 0)):>10.2f} {float(item.get('mid', 0)):>10.2f} {float(item.get('low', 0)):>10.2f}")
        
        elif indicator == 'MA':
            print(f"  {'Date':<12} {'MA5':>10} {'MA10':>10} {'MA20':>10} {'MA60':>10}")
            print(f"  {'-'*60}")
            for item in data:
                print(f"  {item.get('d', 'N/A'):<12} {float(item.get('ma5', 0)):>10.2f} {float(item.get('ma10', 0)):>10.2f} {float(item.get('ma20', 0)):>10.2f} {float(item.get('ma60', 0)):>10.2f}")
        
        # Print JSON for parsing
        print(f"\n##TECH_META##")
        print(json.dumps({
            'code': code,
            'indicator': indicator,
            'count': len(data),
            'data': data
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python zhitu_tech.py <code> <indicator> [days]")
        print("Example: python zhitu_tech.py 000001 MACD")
        print("         python zhitu_tech.py 600519 KDJ 30")
        print("\nIndicators:")
        print("  MACD - Moving Average Convergence Divergence")
        print("  KDJ  - Stochastic Oscillator")
        print("  BOLL - Bollinger Bands")
        print("  MA   - Moving Average")
        sys.exit(1)
    
    code = sys.argv[1]
    indicator = sys.argv[2].upper()
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    get_tech_indicator(code, indicator, days)
