#!/usr/bin/env python3
"""
REITs行情查询
查询REITs实时行情
"""

import akshare as ak
import pandas as pd
import argparse

def get_reits_quote():
    """获取REITs行情"""
    try:
        df = ak.reit_stock_js()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("REITs实时行情")
        print("=" * 90)
        
        # 按涨跌幅排序
        df_sorted = df.sort_values('涨跌幅', ascending=False)
        
        print(f"{'代码':<10} {'名称':<18} {'最新价':<10} {'涨跌幅%':<10} {'成交额(万)':<12}")
        print("-" * 90)
        
        for _, row in df_sorted.head(30).iterrows():
            print(f"{row.get('代码', '--'):<10} {row.get('名称', '--')[:18]:<18} "
                  f"{row.get('最新价', 0):<10.3f} {row.get('涨跌幅', 0):<10.2f} "
                  f"{row.get('成交额', 0)/1e4:<12.1f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

def get_reits_by_type(asset_type):
    """按资产类型查询REITs"""
    try:
        df = ak.reit_stock_js()
        
        filtered = df[df['资产类型'].str.contains(asset_type, na=False)]
        
        if filtered.empty:
            print(f"未找到资产类型为 '{asset_type}' 的REITs")
            return
        
        print("=" * 90)
        print(f"{asset_type}类REITs")
        print("=" * 90)
        
        for _, row in filtered.iterrows():
            print(f"{row.get('代码', '--')} {row.get('名称', '--')} "
                  f"最新价: {row.get('最新价', 0):.3f} "
                  f"涨跌幅: {row.get('涨跌幅', 0):.2f}%")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, help='资产类型 (如: 产业园/仓储物流/高速公路)')
    
    args = parser.parse_args()
    
    if args.type:
        get_reits_by_type(args.type)
    else:
        get_reits_quote()
