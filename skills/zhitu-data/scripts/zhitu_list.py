#!/usr/bin/env python3
"""
Get A-share stock list via 智兔数服 (Zhitu API).

Usage:
    python zhitu_list.py [market]

Example:
    python zhitu_list.py
    python zhitu_list.py sh
    python zhitu_list.py sz

Arguments:
    market: sh (Shanghai), sz (Shenzhen), bj (Beijing), or empty for all
"""

import sys
import json
import requests

API_BASE = "https://api.zhituapi.com"
TOKEN = "ZHITU_TOKEN_LIMIT_TEST"

def get_stock_list(market=None):
    try:
        print(f"\n📋 A-Share Stock List")
        print(f"{'='*80}\n")
        
        # Note: 智兔数服 doesn't have a direct stock list API
        # We'll provide a curated list of popular stocks
        
        stocks = {
            'sh': [
                ('600519.SH', '贵州茅台'),
                ('600036.SH', '招商银行'),
                ('601318.SH', '中国平安'),
                ('600276.SH', '恒瑞医药'),
                ('600887.SH', '伊利股份'),
                ('601398.SH', '工商银行'),
                ('601288.SH', '农业银行'),
                ('600000.SH', '浦发银行'),
                ('601668.SH', '中国建筑'),
                ('600030.SH', '中信证券'),
            ],
            'sz': [
                ('000001.SZ', '平安银行'),
                ('000002.SZ', '万科A'),
                ('000858.SZ', '五粮液'),
                ('000333.SZ', '美的集团'),
                ('002415.SZ', '海康威视'),
                ('300750.SZ', '宁德时代'),
                ('300059.SZ', '东方财富'),
                ('000568.SZ', '泸州老窖'),
                ('002594.SZ', '比亚迪'),
                ('000063.SZ', '中兴通讯'),
            ],
            'bj': [
                ('430047.BJ', '诺思兰德'),
                ('835185.BJ', '贝特瑞'),
                ('832735.BJ', '德源药业'),
            ]
        }
        
        all_stocks = stocks['sh'] + stocks['sz'] + stocks['bj']
        
        if market:
            if market.lower() in stocks:
                display_stocks = stocks[market.lower()]
                print(f"  {market.upper()} Market Stocks ({len(display_stocks)} samples):")
            else:
                print(f"  [ERROR] Invalid market. Use: sh, sz, bj")
                sys.exit(1)
        else:
            display_stocks = all_stocks[:20]
            print(f"  Popular A-Share Stocks ({len(display_stocks)} samples):")
        
        print(f"  {'-'*60}")
        print(f"  {'Code':<15} {'Name':<20} {'Exchange':<10}")
        print(f"  {'-'*60}")
        
        for code, name in display_stocks:
            exchange = 'Shanghai' if '.SH' in code else ('Shenzhen' if '.SZ' in code else 'Beijing')
            print(f"  {code:<15} {name:<20} {exchange:<10}")
        
        if not market:
            print(f"\n  ... and more")
        
        print(f"\n  Usage examples:")
        print(f"    python zhitu_quote.py 600519")
        print(f"    python zhitu_hist.py 000001 20240101 20240312")
        print(f"    python zhitu_tech.py 300750 MACD")
        
        print(f"\n##LIST_META##")
        print(json.dumps({
            'market': market or 'all',
            'count': len(display_stocks),
            'stocks': [{'code': c, 'name': n} for c, n in display_stocks]
        }, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get list: {e}")
        sys.exit(1)

if __name__ == "__main__":
    market = sys.argv[1] if len(sys.argv) > 1 else None
    get_stock_list(market)
