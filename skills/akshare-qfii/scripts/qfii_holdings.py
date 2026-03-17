#!/usr/bin/env python3
"""
QFII持仓查询
查询QFII机构持股数据
"""

import akshare as ak
import pandas as pd
import argparse

def get_qfii_holdings(year=2024, quarter=3):
    """获取QFII持仓"""
    try:
        df = ak.stock_institute_hold_detail(symbol="qfii", year=year, quarter=quarter)
        
        if df.empty:
            print("暂无QFII持仓数据")
            return
        
        print("=" * 90)
        print(f"QFII持仓统计 ({year}年Q{quarter})")
        print("=" * 90)
        
        # 统计
        total_stocks = df['股票代码'].nunique()
        total_institutes = df['机构名称'].nunique()
        
        print(f"\n【持仓概况】")
        print(f"  涉及股票: {total_stocks} 只")
        print(f"  QFII机构: {total_institutes} 家")
        
        # 机构持股排行
        print(f"\n【QFII机构持股数排行】")
        inst_stats = df.groupby('机构名称')['股票代码'].count().sort_values(ascending=False).head(15)
        print(f"{'机构名称':<30} {'持股数量':<10}")
        print("-" * 50)
        for inst, count in inst_stats.items():
            print(f"{inst[:30]:<30} {count:<10}")
        
        # 重仓股
        print(f"\n【QFII重仓股 TOP20】")
        stock_stats = df.groupby(['股票代码', '股票名称']).agg({
            '机构名称': 'count',
            '持股数': 'sum'
        }).reset_index()
        stock_stats.columns = ['代码', '名称', '机构数', '总持股']
        stock_stats = stock_stats.sort_values('机构数', ascending=False).head(20)
        
        print(f"{'代码':<10} {'名称':<12} {'持有机构数':<12} {'总持股(万股)':<15}")
        print("-" * 60)
        for _, row in stock_stats.iterrows():
            print(f"{row['代码']:<10} {row['名称']:<12} {row['机构数']:<12} {row['总持股']/1e4:<15.2f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=2024, help='年份')
    parser.add_argument('--quarter', type=int, default=3, choices=[1,2,3,4], help='季度')
    
    args = parser.parse_args()
    get_qfii_holdings(args.year, args.quarter)
