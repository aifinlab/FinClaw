#!/usr/bin/env python3
"""
FOF基金列表
查询所有FOF基金
"""

import akshare as ak
import pandas as pd

def get_fof_list():
    """获取FOF基金列表"""
    try:
        df = ak.fund_fof_info_em()
        
        if df.empty:
            print("暂无FOF基金数据")
            return
        
        print("=" * 90)
        print("FOF基金列表")
        print("=" * 90)
        
        print(f"{'基金代码':<12} {'基金名称':<25} {'类型':<15} {'成立日期':<12}")
        print("-" * 90)
        
        for _, row in df.head(50).iterrows():
            print(f"{row.get('基金代码', '--'):<12} {row.get('基金简称', '--')[:25]:<25} "
                  f"{row.get('基金类型', '--'):<15} {row.get('成立日期', '--'):<12}")
        
        print("=" * 90)
        print(f"共 {len(df)} 只FOF基金")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_fof_list()
