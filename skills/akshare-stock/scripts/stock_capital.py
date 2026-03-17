#!/usr/bin/env python3
"""
Get stock capital flow (资金流向) data.

Usage:
    python stock_capital.py [options]

Options:
    --market sh|sz       Market filter
    --sort net_inflow    Sort by net inflow (default)
    --limit N            Limit results (default: 20)

Example:
    python stock_capital.py
    python stock_capital.py --market sh --limit 30
"""

import sys
import json
import argparse

def get_capital_flow(market=None, sort_by='net_inflow', limit=20):
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] akshare not installed. Run: pip install akshare")
        sys.exit(1)
    
    try:
        print(f"\n💰 Capital Flow Analysis")
        print(f"{'='*100}")
        
        # Get capital flow data
        if market == 'sh':
            df = ak.stock_sh_a_spot_em()
        elif market == 'sz':
            df = ak.stock_sz_a_spot_em()
        else:
            df = ak.stock_zh_a_spot_em()
        
        # Sort by net inflow (主力净流入)
        if '主力净流入' in df.columns:
            df = df.sort_values('主力净流入', ascending=False)
        
        print(f"  {'No.':<4} {'Code':<8} {'Name':<15} {'Price':<10} {'Change%':<10} {'Net Inflow(万)':<15} {'Main Force':<12}")
        print(f"  {'-'*100}")
        
        results = []
        for idx, (_, row) in enumerate(df.head(limit).iterrows(), 1):
            code = row.get('代码', '')
            name = row.get('名称', '')
            price = row.get('最新价', 0)
            change = row.get('涨跌幅', 0)
            net_inflow = row.get('主力净流入', 0)
            
            # Determine main force direction
            if net_inflow > 0:
                force_emoji = "🟢 In"
            elif net_inflow < 0:
                force_emoji = "🔴 Out"
            else:
                force_emoji = "⚪ Neutral"
            
            print(f"  {idx:<4} {code:<8} {name:<15} {price:<10.2f} {change:>+8.2f}% {net_inflow/10000:>+13.2f} {force_emoji:<12}")
            results.append({
                'index': idx,
                'code': code,
                'name': name,
                'price': price,
                'change_pct': change,
                'net_inflow': net_inflow,
                'main_force': 'in' if net_inflow > 0 else ('out' if net_inflow < 0 else 'neutral')
            })
        
        # Summary
        total_inflow = sum(r['net_inflow'] for r in results if r['net_inflow'] > 0)
        total_outflow = sum(r['net_inflow'] for r in results if r['net_inflow'] < 0)
        
        print(f"\n  Summary:")
        print(f"    Top {limit} Net Inflow: {total_inflow/10000:+.2f}万")
        print(f"    Top {limit} Net Outflow: {total_outflow/10000:+.2f}万")
        
        # Print JSON for parsing
        print(f"\n##CAPITAL_META##")
        print(json.dumps({
            'market': market or 'all',
            'count': len(results),
            'total_inflow': total_inflow,
            'total_outflow': total_outflow,
            'data': results
        }, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get capital flow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get capital flow data')
    parser.add_argument('--market', choices=['sh', 'sz'], help='Market filter')
    parser.add_argument('--sort', default='net_inflow', help='Sort field')
    parser.add_argument('--limit', type=int, default=20, help='Limit results (default: 20)')
    
    args = parser.parse_args()
    
    get_capital_flow(market=args.market, sort_by=args.sort, limit=args.limit)
