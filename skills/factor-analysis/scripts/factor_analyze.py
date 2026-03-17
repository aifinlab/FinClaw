#!/usr/bin/env python3
"""
多因子分析
分析股票因子有效性
"""

import akshare as ak
import pandas as pd

def analyze_factor(factor='pe'):
    """分析因子"""
    print("=" * 70)
    print(f"因子分析 - {factor}")
    print("=" * 70)
    
    try:
        # 获取股票列表
        df = ak.stock_zh_a_spot_em()
        
        if factor == 'pe':
            df_sorted = df.sort_values('市盈率')
            print("\n【市盈率最低TOP20】")
            for _, row in df_sorted.head(20).iterrows():
                print(f"{row['代码']} {row['名称']}: PE={row['市盈率']:.2f}")
        
        elif factor == 'pb':
            df_sorted = df.sort_values('市净率')
            print("\n【市净率最低TOP20】")
            for _, row in df_sorted.head(20).iterrows():
                print(f"{row['代码']} {row['名称']}: PB={row['市净率']:.2f}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    analyze_factor()
