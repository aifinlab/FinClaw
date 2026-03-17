#!/usr/bin/env python3
"""
Get sector/industry data via AkShare (East Money).

Usage:
    python stock_sector.py [sector_name]

Example:
    python stock_sector.py                    # List all sectors
    python stock_sector.py 半导体               # Get specific sector
    python stock_sector.py 银行

Popular sectors:
    半导体, 银行, 白酒, 新能源, 医药, 房地产, 汽车, 人工智能
"""

import sys
import json
import argparse

def get_sectors():
    """Get all available sectors"""
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] akshare not installed. Run: pip install akshare")
        sys.exit(1)
    
    try:
        # Get sector list
        df = ak.stock_board_industry_name_em()
        
        print("\n📊 Available Sectors/Industries")
        print(f"{'='*60}")
        print(f"  {'No.':<4} {'Sector Name':<30} {'Change%':<10}")
        print(f"  {'-'*60}")
        
        results = []
        for idx, (_, row) in enumerate(df.iterrows(), 1):
            name = row.get('板块名称', '')
            change = row.get('涨跌幅', 0)
            
            print(f"  {idx:<4} {name:<30} {change:>+8.2f}%")
            results.append({
                'index': idx,
                'name': name,
                'change_pct': change
            })
        
        print(f"\n  Total: {len(results)} sectors")
        
        print(f"\n##SECTOR_META##")
        print(json.dumps({'count': len(results), 'sectors': results[:50]}, ensure_ascii=False))
        
    except Exception as e:
        print(f"[ERROR] Failed to get sectors: {e}")
        sys.exit(1)

def get_sector_stocks(sector_name, limit=30):
    """Get stocks in a specific sector"""
    try:
        import akshare as ak
    except ImportError:
        print("[ERROR] akshare not installed. Run: pip install akshare")
        sys.exit(1)
    
    try:
        # Get stocks in sector
        df = ak.stock_board_industry_cons_em(symbol=sector_name)
        
        print(f"\n📊 {sector_name} Sector - Top Stocks")
        print(f"{'='*80}")
        print(f"  {'No.':<4} {'Code':<8} {'Name':<15} {'Price':<10} {'Change%':<10} {'Volume':<12}")
        print(f"  {'-'*80}")
        
        results = []
        for idx, (_, row) in enumerate(df.head(limit).iterrows(), 1):
            code = row.get('代码', '')
            name = row.get('名称', '')
            price = row.get('最新价', 0)
            change = row.get('涨跌幅', 0)
            volume = row.get('成交额', 0)
            
            print(f"  {idx:<4} {code:<8} {name:<15} {price:<10.2f} {change:>+8.2f}% {volume:<12.0f}")
            results.append({
                'index': idx,
                'code': code,
                'name': name,
                'price': price,
                'change_pct': change,
                'amount': volume
            })
        
        # Calculate sector stats
        avg_change = df['涨跌幅'].mean() if '涨跌幅' in df.columns else 0
        up_count = len(df[df['涨跌幅'] > 0]) if '涨跌幅' in df.columns else 0
        down_count = len(df[df['涨跌幅'] < 0]) if '涨跌幅' in df.columns else 0
        
        print(f"\n  Sector Stats:")
        print(f"    Average Change: {avg_change:+.2f}%")
        print(f"    Up: {up_count} | Down: {down_count} | Flat: {len(df) - up_count - down_count}")
        
        print(f"\n##SECTOR_STOCKS_META##")
        print(json.dumps({
            'sector': sector_name,
            'avg_change': round(avg_change, 2),
            'up_count': up_count,
            'down_count': down_count,
            'count': len(results),
            'stocks': results
        }, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"[ERROR] Failed to get sector stocks: {e}")
        print(f"[INFO] Try running without sector name to see available sectors")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get sector/industry data')
    parser.add_argument('sector', nargs='?', help='Sector name (optional)')
    parser.add_argument('--limit', type=int, default=30, help='Limit results (default: 30)')
    
    args = parser.parse_args()
    
    if args.sector:
        get_sector_stocks(args.sector, limit=args.limit)
    else:
        get_sectors()
