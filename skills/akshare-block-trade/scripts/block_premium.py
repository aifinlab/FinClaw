#!/usr/bin/env python3
"""
大宗交易折溢价分析
分析大宗交易的折溢价情况
"""

import akshare as ak
import pandas as pd

def analyze_premium():
    """分析折溢价情况"""
    try:
        df = ak.stock_dzjy_mrtj()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("大宗交易折溢价分析")
        print("=" * 90)
        
        # 整体统计
        avg_premium = df['折溢价率'].mean()
        median_premium = df['折溢价率'].median()
        
        print(f"\n【整体统计】")
        print(f"  平均折溢价率: {avg_premium:.2f}%")
        print(f"  中位数: {median_premium:.2f}%")
        print(f"  最高溢价: {df['折溢价率'].max():.2f}%")
        print(f"  最高折价: {df['折溢价率'].min():.2f}%")
        
        # 溢价排行
        print(f"\n【溢价成交 TOP15】")
        premium_df = df[df['折溢价率'] > 0].sort_values('折溢价率', ascending=False).head(15)
        print(f"{'代码':<10} {'名称':<12} {'溢价率%':<10} {'成交额(万)':<12}")
        print("-" * 60)
        for _, row in premium_df.iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{row['折溢价率']:<10.2f} {row['成交额(万元)']:<12.1f}")
        
        # 折价排行
        print(f"\n【折价成交 TOP15】")
        discount_df = df[df['折溢价率'] < 0].sort_values('折溢价率', ascending=True).head(15)
        print(f"{'代码':<10} {'名称':<12} {'折价率%':<10} {'成交额(万)':<12}")
        print("-" * 60)
        for _, row in discount_df.iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{row['折溢价率']:<10.2f} {row['成交额(万元)']:<12.1f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    analyze_premium()
