#!/usr/bin/env python3
"""
美联储利率数据
查询美联储关键利率
"""

import akshare as ak
import pandas as pd

def get_fed_rate():
    """获取美联储利率"""
    try:
        # 使用AkShare的美债收益率作为参考
        df = ak.bond_us_usd()
        
        print("=" * 70)
        print("美联储利率与美债收益率")
        print("=" * 70)
        
        for _, row in df.head(10).iterrows():
            print(f"{row.get('名称', '--')}: {row.get('收益率', '--')}%")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_fed_rate()
