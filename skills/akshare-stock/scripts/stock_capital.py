#!/usr/bin/env python3
"""
Get stock capital flow (资金流向) data.

Usage:
    # 获取市场资金流向排行
    python stock_capital.py [options]
    python stock_capital.py --market sh --limit 30

    # 查询特定股票的资金流向
    python stock_capital.py 600519 000858 300750
    python stock_capital.py --stocks 600519,000858,300750

Options:
    --market sh|sz       Market filter
    --sort net_inflow    Sort by net inflow (default)
    --limit N            Limit results (default: 20)
    --stocks CODE,..     Comma-separated stock codes
"""

import sys
import traceback
import akshare as ak
import argparse
import json


def get_capital_flow(
    market=None,
    sort_by='net_inflow',
    limit=20,
        stock_codes=None):
    """
    获取资金流向数据

    Args:
        market: 市场筛选 (sh/sz/None)
        sort_by: 排序字段
        limit: 结果数量限制
        stock_codes: 特定股票代码列表
    """
    try:
        print(f"\n💰 Capital Flow Analysis")
        print(f"{'=' *100}")

        # Get capital flow data
        if market == 'sh':
            df = ak.stock_sh_a_spot_em()
        elif market == 'sz':
            df = ak.stock_sz_a_spot_em()
        else:
            df = ak.stock_zh_a_spot_em()

        # If specific stocks requested, filter
        if stock_codes and len(stock_codes) > 0:
            print(
    f"  Querying {
        len(stock_codes)} specific stocks: {
            ', '.join(stock_codes)}")
            df = df[df['代码'].isin(stock_codes)]
            if df.empty:
                print(f"  [WARNING] No data found for specified stocks")
                return []
        else:
            # Sort by net inflow (主力净流入)
            if '主力净流入' in df.columns:
                df = df.sort_values('主力净流入', ascending=False)
            df = df.head(limit)

        print(
    f"  {
        'No.':<4} {
            'Code':<8} {
                'Name':<15} {
                    'Price':<10} {
                        'Change%':<10} {
                            'Net Inflow(万)':<15} {
                                'Main Force':<12}")
        print(f"  {'-' *100}")

        results = []
        for idx, (_, row) in enumerate(df.iterrows(), 1):
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

            print(f"  {idx:<4} {code:<8} {name:<15} {price:<10.2f} {change:>+8.2f}% {net_inflow /10000:>+13.2f} {force_emoji:<12}")
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
        if results:
            total_inflow = sum(r['net_inflow']
                                for r in results if r['net_inflow'] > 0)
            total_outflow = sum(r['net_inflow']
                                for r in results if r['net_inflow'] < 0)

            print(f"\n  Summary:")
            print(f"    Total Inflow: {total_inflow /10000:+.2f}万")
            print(f"    Total Outflow: {total_outflow /10000:+.2f}万")

            # Print JSON for parsing
            print(f"\n  # CAPITAL_META##")
            print(json.dumps({
                'market': market or 'all',
                'count': len(results),
                'total_inflow': total_inflow,
                'total_outflow': total_outflow,
                'data': results
            }, ensure_ascii=False, default=str))

        return results

    except Exception as e:
        print(f"[ERROR] Failed to get capital flow: {e}")
        traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get capital flow data')
    parser.add_argument(
    'codes',
    nargs='*',
        help='Stock codes to query (e.g., 600519 000858)')
    parser.add_argument('--market', choices=['sh', 'sz'], help='Market filter')
    parser.add_argument('--sort', default='net_inflow', help='Sort field')
    parser.add_argument('--limit', type=int, default=20,
                        help='Limit results (default: 20)')
    parser.add_argument(
    '--stocks',
        help='Comma-separated stock codes (e.g., 600519,000858)')

    args = parser.parse_args()

    # Build stock codes list
    stock_codes = []
    if args.codes:
        stock_codes.extend(args.codes)
    if args.stocks:
        stock_codes.extend([c.strip() for c in args.stocks.split(',')])

    get_capital_flow(
        market=args.market,
        sort_by=args.sort,
        limit=args.limit,
        stock_codes=stock_codes if stock_codes else None
    )
