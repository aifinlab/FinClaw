#!/usr/bin/env python3
"""
科创板股票列表
查询所有科创板股票
"""

import akshare as ak
import pandas as pd

def get_star_list():
    """获取科创板股票列表"""
    try:
        df = ak.stock_zh_kcb_spot()
        
        if df.empty:
            print("暂无科创板数据")
            return
        
        print("=" * 90)
        print("科创板股票列表")
        print("=" * 90)
        
        print(f"{'代码':<10} {'名称':<12} {'最新价':<10} {'涨跌幅%':<10} {'市值(亿)':<12}")
        print("-" * 90)
        
        for _, row in df.head(30).iterrows():
            market_cap = row.get('总市值', 0) / 1e8
            print(f"{row['代码']:<10} {row['名称']:<12} "
                  f"{row['最新价']:<10.2f} {row['涨跌幅']:<10.2f} "
                  f"{market_cap:<12.1f}")
        
        print("=" * 90)
        print(f"共 {len(df)} 只科创板股票")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_star_list()
