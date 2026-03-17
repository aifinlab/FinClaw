#!/usr/bin/env python3
"""
欧元区经济数据
查询欧元区关键经济指标
"""

import akshare as ak

def get_ecb_data():
    """获取欧央行数据"""
    try:
        # 获取欧元区CPI
        df = ak.macro_euro_cpi_monthly()
        
        print("=" * 70)
        print("欧元区CPI数据")
        print("=" * 70)
        
        print(f"{'日期':<12} {'CPI同比%':<12}")
        print("-" * 30)
        
        for _, row in df.head(12).iterrows():
            print(f"{row.get('日期', '--'):<12} {row.get('同比', '--'):<12}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_ecb_data()
