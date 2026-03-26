#!/usr/bin/env python3
"""
美国CPI数据 - 使用AkShare获取美国通胀数据
"""

import akshare as ak


def get_us_cpi():
    """获取美国CPI数据"""
    try:
        df = ak.macro_usa_cpi_monthly()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 70)
        print("美国CPI月度数据")
        print("=" * 70)
        print(f"{'日期':<15} {'CPI同比%':<12} {'CPI环比%':<12}")
        print("-" * 40)
        
        for _, row in df.head(12).iterrows():
            date = row.get('日期', '--')
            yoy = row.get('CPI同比%', '--')
            mom = row.get('CPI环比%', '--')
            print(f"{date:<15} {yoy:<12} {mom:<12}")
        
        print("=" * 70)
    except Exception as e:
        print(f"获取数据失败: {e}")


if __name__ == "__main__":
    get_us_cpi()
