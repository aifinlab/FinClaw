#!/usr/bin/env python3
"""
雪球热股榜
查询雪球热股排行
"""

import akshare as ak
import pandas as pd

def get_xueqiu_hot():
    """获取雪球热股榜"""
    try:
        df = ak.stock_xq_hot_trend()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("雪球热股榜")
        print("=" * 90)
        
        print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'热度':<10} {'涨跌幅%':<10}")
        print("-" * 60)
        
        for i, (_, row) in enumerate(df.head(30).iterrows(), 1):
            print(f"{i:<6} {row.get('股票代码', '--'):<10} {row.get('股票名称', '--'):<12} "
                  f"{row.get('热度', '--'):<10} {row.get('涨跌幅', '--'):<10}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_xueqiu_hot()
