#!/usr/bin/env python3
"""
个股融资融券数据查询
查询指定股票的融资融券明细数据
"""

import akshare as ak
import pandas as pd
import argparse
from datetime import datetime

def get_stock_margin(code):
    """获取个股融资融券数据"""
    try:
        # 获取个股融资融券数据
        df = ak.stock_margin_detail_szse(date="")
        
        # 筛选指定股票
        stock_data = df[df['证券代码'] == code]
        
        if stock_data.empty:
            # 尝试上海市场
            df_sh = ak.stock_margin_detail_shse(date="")
            stock_data = df_sh[df_sh['证券代码'] == code]
            market = "上海"
        else:
            market = "深圳"
        
        if stock_data.empty:
            print(f"未找到股票 {code} 的融资融券数据")
            return
        
        # 获取股票名称
        stock_name = stock_data.iloc[0]['证券简称']
        
        print("=" * 70)
        print(f"{stock_name} ({code}) 融资融券数据")
        print(f"市场: {market} | 数据日期: {stock_data.iloc[0]['日期']}")
        print("=" * 70)
        
        data = stock_data.iloc[0]
        
        print("\n【融资数据】")
        print(f"  融资余额:        {data['融资余额']:,.0f} 元")
        print(f"  融资买入额:      {data['融资买入额']:,.0f} 元")
        print(f"  融资偿还额:      {data['融资偿还额']:,.0f} 元")
        
        if data['融资偿还额'] > 0:
            net_buy = data['融资买入额'] - data['融资偿还额']
            print(f"  融资净买入:      {net_buy:,.0f} 元 ({'+' if net_buy > 0 else ''}{net_buy/1e4:.1f}万)")
        
        print("\n【融券数据】")
        print(f"  融券余额:        {data['融券余额']:,.0f} 元")
        print(f"  融券卖出量:      {data['融券卖出量']:,.0f} 股")
        print(f"  融券偿还量:      {data['融券偿还量']:,.0f} 股")
        
        print("\n【融资融券合计】")
        print(f"  融资融券余额:    {data['融资融券余额']:,.0f} 元")
        print(f"                   ({data['融资融券余额']/1e8:.2f} 亿元)")
        
        # 计算杠杆比例参考
        print("\n【杠杆水平参考】")
        print(f"  该股票融资融券余额占总市场比例: 需结合总市值计算")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取数据失败: {e}")

def search_margin_stocks(keyword):
    """搜索两融标的股票"""
    try:
        # 获取融资融券标的列表
        df_sz = ak.stock_margin_detail_szse(date="")
        
        # 搜索股票名称
        results = df_sz[df_sz['证券简称'].str.contains(keyword, na=False)]
        
        if results.empty:
            print(f"未找到包含 '{keyword}' 的两融标的股票")
            return
        
        print("=" * 70)
        print(f"搜索结果: '{keyword}'")
        print("=" * 70)
        print(f"{'代码':<10} {'名称':<12} {'融资余额(亿)':<15} {'融券余额(亿)':<15}")
        print("-" * 70)
        
        for _, row in results.head(20).iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{row['融资余额']/1e8:<15.2f} {row['融券余额']/1e8:<15.2f}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"搜索失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='个股融资融券数据查询')
    parser.add_argument('--code', type=str, help='股票代码 (如: 000001)')
    parser.add_argument('--search', type=str, help='搜索关键词')
    
    args = parser.parse_args()
    
    if args.search:
        search_margin_stocks(args.search)
    elif args.code:
        get_stock_margin(args.code)
    else:
        print("用法示例:")
        print("  python margin_stock.py --code 000001")
        print("  python margin_stock.py --search 平安")
