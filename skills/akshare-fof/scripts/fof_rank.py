#!/usr/bin/env python3
"""
FOF基金业绩排行
查询FOF基金业绩排行
"""

import akshare as ak
import pandas as pd
import argparse

def get_fof_rank(period='1y'):
    """获取FOF业绩排行"""
    try:
        # 获取FOF收益排行
        df = ak.fund_fof_rank_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        # 根据周期选择列
        period_map = {
            '1m': '近1月',
            '3m': '近3月', 
            '6m': '近6月',
            '1y': '近1年',
            '2y': '近2年',
            '3y': '近3年'
        }
        
        period_name = period_map.get(period, '近1年')
        
        print("=" * 90)
        print(f"FOF基金业绩排行 ({period_name})")
        print("=" * 90)
        
        # 排序
        df_sorted = df.sort_values(period_name, ascending=False)
        
        print(f"{'排名':<6} {'代码':<12} {'名称':<25} {'{period_name}':<12} {'成立日期':<12}")
        print("-" * 90)
        
        for i, (_, row) in enumerate(df_sorted.head(30).iterrows(), 1):
            print(f"{i:<6} {row['基金代码']:<12} {row['基金简称'][:25]:<25} "
                  f"{row.get(period_name, '--'):<12} {row.get('成立日期', '--'):<12}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

def get_pension_fund():
    """获取养老目标基金"""
    try:
        df = ak.fund_fof_info_em()
        
        # 筛选养老目标基金
        pension_df = df[df['基金简称'].str.contains('养老|目标日期', na=False)]
        
        if pension_df.empty:
            print("暂无养老目标基金数据")
            return
        
        print("=" * 90)
        print("养老目标基金列表")
        print("=" * 90)
        
        print(f"{'基金代码':<12} {'基金名称':<30} {'类型':<15} {'成立日期':<12}")
        print("-" * 90)
        
        for _, row in pension_df.iterrows():
            print(f"{row.get('基金代码', '--'):<12} {row.get('基金简称', '--')[:30]:<30} "
                  f"{row.get('基金类型', '--'):<15} {row.get('成立日期', '--'):<12}")
        
        print("=" * 90)
        print(f"共 {len(pension_df)} 只养老目标基金")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--period', type=str, default='1y', 
                       choices=['1m', '3m', '6m', '1y', '2y', '3y'],
                       help='业绩周期')
    parser.add_argument('--pension', action='store_true', help='养老目标基金')
    
    args = parser.parse_args()
    
    if args.pension:
        get_pension_fund()
    else:
        get_fof_rank(args.period)
