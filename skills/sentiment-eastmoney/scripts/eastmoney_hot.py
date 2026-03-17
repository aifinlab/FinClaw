#!/usr/bin/env python3
"""
东财股吧热度
查询东方财富股吧热度排行
"""

import akshare as ak
import pandas as pd

def get_eastmoney_hot():
    """获取东财热度"""
    try:
        # 获取成交量排行作为热度参考
        df = ak.stock_zh_a_spot_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        # 按成交额排序
        df_sorted = df.sort_values('成交额', ascending=False)
        
        print("=" * 90)
        print("东方财富热度排行 (成交额)")
        print("=" * 90)
        
        print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'成交额(亿)':<12} {'涨跌幅%':<10}")
        print("-" * 60)
        
        for i, (_, row) in enumerate(df_sorted.head(30).iterrows(), 1):
            print(f"{i:<6} {row['代码']:<10} {row['名称']:<12} "
                  f"{row['成交额']/1e8:<12.2f} {row['涨跌幅']:<10.2f}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_eastmoney_hot()
