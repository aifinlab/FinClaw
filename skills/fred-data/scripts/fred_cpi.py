#!/usr/bin/env python3
"""
美国CPI数据
查询美国通胀数据
"""

import akshare as ak
import pandas as pd

def get_us_cpi():
    """获取美国CPI"""
    try:
        # 获取宏观数据
        df = ak.macro_usa_cpi_monthly()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 70)
        print("美国CPI月度数据")
        print("=" * 70)
        
        print(f"{'日期':<12} {'CPI同比%':<12} {'CPI环比%':<12}")
        print("-" * 40)
        
        for _, row in df.head(12).iterrows():
            print(f"{row.get('日期', '--'):<12} {row.get('同比', '--'):<12} {row.get('环比', '--'):<12}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_us_cpi()
