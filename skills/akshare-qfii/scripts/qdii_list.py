#!/usr/bin/env python3
"""
QDII基金列表
查询所有QDII基金
"""

import akshare as ak
import pandas as pd

def get_qdii_list():
    """获取QDII基金列表"""
    try:
        df = ak.fund_etf_category_sina(symbol="QDII_ETF")
        
        if df.empty:
            print("暂无QDII基金数据")
            return
        
        print("=" * 90)
        print("QDII基金列表")
        print("=" * 90)
        
        print(f"{'基金代码':<12} {'基金名称':<30} {'最新价':<10} {'涨跌幅%':<10}")
        print("-" * 90)
        
        for _, row in df.head(50).iterrows():
            change = row.get('涨跌幅', 0)
            print(f"{row.get('代码', '--'):<12} {row.get('名称', '--')[:30]:<30} "
                  f"{row.get('最新价', 0):<10.3f} {change:<10.2f}")
        
        print("=" * 90)
        print(f"共 {len(df)} 只QDII基金")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_qdii_list()
