#!/usr/bin/env python3
"""
REITs基金列表
查询所有公募REITs
"""

import akshare as ak
import pandas as pd

def get_reits_list():
    """获取REITs列表"""
    try:
        df = ak.reit_stock_js()
        
        if df.empty:
            print("暂无REITs数据")
            return
        
        print("=" * 90)
        print("公募REITs列表")
        print("=" * 90)
        
        print(f"{'代码':<10} {'名称':<20} {'最新价':<10} {'涨跌幅%':<10} {'资产类型':<15}")
        print("-" * 90)
        
        for _, row in df.head(50).iterrows():
            print(f"{row.get('代码', '--'):<10} {row.get('名称', '--')[:20]:<20} "
                  f"{row.get('最新价', 0):<10.3f} {row.get('涨跌幅', 0):<10.2f} "
                  f"{row.get('资产类型', '--'):<15}")
        
        print("=" * 90)
        print(f"共 {len(df)} 只REITs")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_reits_list()
