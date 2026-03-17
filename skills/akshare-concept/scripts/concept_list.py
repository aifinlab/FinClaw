#!/usr/bin/env python3
"""
概念板块列表
查询所有概念板块
"""

import akshare as ak
import pandas as pd

def get_concept_list():
    """获取概念板块列表"""
    try:
        df = ak.stock_board_concept_name_em()
        
        if df.empty:
            print("暂无数据")
            return
        
        print("=" * 90)
        print("概念板块列表")
        print("=" * 90)
        
        print(f"{'板块名称':<20} {'最新价':<10} {'涨跌幅%':<10} {'涨跌额':<10} {'换手率%':<10}")
        print("-" * 90)
        
        for _, row in df.head(50).iterrows():
            change = row.get('涨跌幅', 0)
            change_str = f"{change:+.2f}" if change else "--"
            
            print(f"{row['板块名称']:<20} {row.get('最新价', 0):<10.2f} "
                  f"{change_str:<10} {row.get('涨跌额', 0):<10.2f} "
                  f"{row.get('换手率', 0):<10.2f}")
        
        print("=" * 90)
        print(f"共 {len(df)} 个概念板块")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    get_concept_list()
