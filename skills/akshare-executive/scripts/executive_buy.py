#!/usr/bin/env python3
"""
高管增持排行
统计高管净增持排行
"""

import akshare as ak
import pandas as pd

def get_executive_buy_rank():
    """获取高管增持排行"""
    try:
        df = ak.stock_ggcg_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        # 筛选增持
        buy_df = df[df['变动方向'].str.contains('增持', na=False)]
        
        # 按股票汇总
        buy_summary = buy_df.groupby(['股票代码', '股票简称']).agg({
            '变动股数': 'sum'
        }).reset_index().sort_values('变动股数', ascending=False)
        
        print("=" * 70)
        print("高管增持排行")
        print("=" * 70)
        
        print(f"{'代码':<10} {'名称':<12} {'增持股数':<15}")
        print("-" * 70)
        
        for _, row in buy_summary.head(30).iterrows():
            print(f"{row['股票代码']:<10} {row['股票简称']:<12} {row['变动股数']:<15.0f}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_executive_buy_rank()
