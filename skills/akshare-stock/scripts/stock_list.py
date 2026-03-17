#!/usr/bin/env python3
"""
Get A-share stock list with filtering options.

Usage:
    python stock_list.py [options]

Options:
    --market sh|sz|bj     Filter by market (Shanghai/Shenzhen/Beijing)
    --type etf|lof        Filter by fund type
    --limit N             Limit results (default: 50)

Example:
    python stock_list.py
    python stock_list.py --market sh
    python stock_list.py --type etf --limit 20
"""

import sys
import json
import argparse

def get_stock_list(market=None, stock_type=None, limit=50):
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] akshare not installed. Run: pip install akshare")
        sys.exit(1)
    
    try:
        print(f"\n📋 A-Share Stock List")
        print(f"{'='*80}")
        
        results = []
        
        if stock_type == 'etf':
            # Get ETF list
            df = ak.fund_etf_spot_em()
            print(f"  ETF List (Top {limit}):")
            print(f"  {'No.':<4} {'Code':<8} {'Name':<20} {'Price':<10} {'Change%':<10}")
            print(f"  {'-'*80}")
            
            for idx, (_, row) in enumerate(df.head(limit).iterrows(), 1):
                code = row.get('代码', '')
                name = row.get('名称', '')
                price = row.get('最新价', 0)
                change = row.get('涨跌幅', 0)
                
                print(f"  {idx:<4} {code:<8} {name:<20} {price:<10.3f} {change:<10.2f}%")
                results.append({
                    'index': idx,
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': change,
                    'type': 'ETF'
                })
                
        elif stock_type == 'lof':
            # Get LOF list
            df = ak.fund_lof_spot_em()
            print(f"  LOF List (Top {limit}):")
            print(f"  {'No.':<4} {'Code':<8} {'Name':<20} {'Price':<10} {'Change%':<10}")
            print(f"  {'-'*80}")
            
            for idx, (_, row) in enumerate(df.head(limit).iterrows(), 1):
                code = row.get('代码', '')
                name = row.get('名称', '')
                price = row.get('最新价', 0)
                change = row.get('涨跌幅', 0)
                
                print(f"  {idx:<4} {code:<8} {name:<20} {price:<10.3f} {change:<10.2f}%")
                results.append({
                    'index': idx,
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': change,
                    'type': 'LOF'
                })
        else:
            # Get all A-share stocks
            df = ak.stock_zh_a_spot_em()
            
            # Filter by market if specified
            if market:
                if market == 'sh':
                    df = df[df['代码'].str.startswith('6')]
                elif market == 'sz':
                    df = df[df['代码'].str.startswith('0') | df['代码'].str.startswith('3')]
                elif market == 'bj':
                    df = df[df['代码'].str.startswith('8') | df['代码'].str.startswith('4')]
            
            market_name = {'sh': 'Shanghai', 'sz': 'Shenzhen', 'bj': 'Beijing'}.get(market, 'All')
            print(f"  {market_name} A-Share List (Top {limit}):")
            print(f"  {'No.':<4} {'Code':<8} {'Name':<20} {'Price':<10} {'Change%':<10} {'Volume':<12}")
            print(f"  {'-'*80}")
            
            for idx, (_, row) in enumerate(df.head(limit).iterrows(), 1):
                code = row.get('代码', '')
                name = row.get('名称', '')
                price = row.get('最新价', 0)
                change = row.get('涨跌幅', 0)
                volume = row.get('成交量', 0)
                
                print(f"  {idx:<4} {code:<8} {name:<20} {price:<10.2f} {change:<10.2f}% {volume:<12,}")
                results.append({
                    'index': idx,
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': change,
                    'volume': volume,
                    'type': 'Stock'
                })
        
        print(f"\n  Total: {len(results)} items")
        
        # Print JSON for parsing
        print(f"\n##LIST_META##")
        print(json.dumps({
            'market': market or 'all',
            'type': stock_type or 'stock',
            'count': len(results),
            'data': results
        }, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get stock list: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get A-share stock list')
    parser.add_argument('--market', choices=['sh', 'sz', 'bj'], help='Market filter')
    parser.add_argument('--type', choices=['etf', 'lof'], help='Type filter')
    parser.add_argument('--limit', type=int, default=50, help='Limit results (default: 50)')
    
    args = parser.parse_args()
    
    get_stock_list(market=args.market, stock_type=args.type, limit=args.limit)
