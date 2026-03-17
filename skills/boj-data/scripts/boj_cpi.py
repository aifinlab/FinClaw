#!/usr/bin/env python3
"""
日本经济数据
查询日本关键经济指标
"""

import akshare as ak

def get_boj_data():
    """获取日央行数据"""
    try:
        df = ak.macro_japan_cpi_monthly()
        
        print("=" * 70)
        print("日本CPI数据")
        print("=" * 70)
        
        print(f"{'日期':<12} {'CPI同比%':<12}")
        print("-" * 30)
        
        for _, row in df.head(12).iterrows():
            print(f"{row.get('日期', '--'):<12} {row.get('同比', '--'):<12}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_boj_data()
