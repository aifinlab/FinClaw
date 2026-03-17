#!/usr/bin/env python3
"""
融资融券排行查询
获取融资买入/偿还排行、融券卖出排行
"""

import akshare as ak
import pandas as pd
import argparse

def get_margin_rank(rank_type='buy', market='sz', limit=20):
    """
    获取融资融券排行
    
    Args:
        rank_type: 'buy' 融资买入排行, 'sell' 融券卖出排行
        market: 'sz' 深圳, 'sh' 上海
        limit: 返回数量
    """
    try:
        # 获取融资融券明细数据
        if market == 'sz':
            df = ak.stock_margin_detail_szse(date="")
            market_name = "深圳"
        else:
            df = ak.stock_margin_detail_shse(date="")
            market_name = "上海"
        
        if df.empty:
            print(f"暂无{market_name}市场融资融券数据")
            return
        
        print("=" * 80)
        
        if rank_type == 'buy':
            # 融资买入排行
            df_sorted = df.sort_values('融资买入额', ascending=False).head(limit)
            print(f"{market_name}市场 融资买入额排行 TOP{limit}")
            print("=" * 80)
            print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'买入额(万)':<15} {'余额(亿)':<12}")
            print("-" * 80)
            
            for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
                print(f"{i:<6} {row['证券代码']:<10} {row['证券简称']:<12} "
                      f"{row['融资买入额']/1e4:<15.1f} {row['融资余额']/1e8:<12.2f}")
        
        elif rank_type == 'sell':
            # 融券卖出排行
            df_sorted = df.sort_values('融券卖出量', ascending=False).head(limit)
            print(f"{market_name}市场 融券卖出量排行 TOP{limit}")
            print("=" * 80)
            print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'卖出量(万股)':<15} {'余额(万)':<12}")
            print("-" * 80)
            
            for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
                print(f"{i:<6} {row['证券代码']:<10} {row['证券简称']:<12} "
                      f"{row['融券卖出量']/1e4:<15.1f} {row['融券余额']/1e4:<12.1f}")
        
        elif rank_type == 'balance':
            # 融资余额排行
            df_sorted = df.sort_values('融资余额', ascending=False).head(limit)
            print(f"{market_name}市场 融资余额排行 TOP{limit}")
            print("=" * 80)
            print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'融资余额(亿)':<15} {'占总市值%':<12}")
            print("-" * 80)
            
            for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
                print(f"{i:<6} {row['证券代码']:<10} {row['证券简称']:<12} "
                      f"{row['融资余额']/1e8:<15.2f} {'--':<12}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"获取排行数据失败: {e}")

def get_net_buy_rank(market='sz', limit=20):
    """获取融资净买入排行"""
    try:
        if market == 'sz':
            df = ak.stock_margin_detail_szse(date="")
            market_name = "深圳"
        else:
            df = ak.stock_margin_detail_shse(date="")
            market_name = "上海"
        
        if df.empty:
            print(f"暂无{market_name}市场数据")
            return
        
        # 计算净买入
        df['净买入'] = df['融资买入额'] - df['融资偿还额']
        df_sorted = df.sort_values('净买入', ascending=False).head(limit)
        
        print("=" * 80)
        print(f"{market_name}市场 融资净买入排行 TOP{limit}")
        print("=" * 80)
        print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'净买入(万)':<15} {'余额(亿)':<12}")
        print("-" * 80)
        
        for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
            net_buy = row['净买入'] / 1e4
            print(f"{i:<6} {row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{net_buy:<15.1f} {row['融资余额']/1e8:<12.2f}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='融资融券排行查询')
    parser.add_argument('--type', type=str, default='buy', 
                       choices=['buy', 'sell', 'balance', 'net'],
                       help='排行类型: buy=融资买入, sell=融券卖出, balance=融资余额, net=净买入')
    parser.add_argument('--market', type=str, default='sz', choices=['sz', 'sh'],
                       help='市场: sz=深圳, sh=上海')
    parser.add_argument('--limit', type=int, default=20, help='返回数量 (默认20)')
    
    args = parser.parse_args()
    
    if args.type == 'net':
        get_net_buy_rank(args.market, args.limit)
    else:
        get_margin_rank(args.type, args.market, args.limit)
