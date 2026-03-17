#!/usr/bin/env python3
"""
机构调研排行
统计调研热度排行
"""

import akshare as ak
import pandas as pd

def get_survey_rank():
    """获取调研热度排行"""
    try:
        df = ak.stock_jgdy_tj_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("机构调研热度排行 (近一年)")
        print("=" * 90)
        
        print(f"{'代码':<10} {'名称':<12} {'调研次数':<10} {'调研机构数':<12} {'行业':<15}")
        print("-" * 90)
        
        for _, row in df.head(30).iterrows():
            print(f"{row['股票代码']:<10} {row['股票简称']:<12} "
                  f"{row['调研次数']:<10} {row['调研机构家数']:<12} "
                  f"{row.get('所属行业', '--'):<15}")
        
        print("=" * 90)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_survey_rank()
