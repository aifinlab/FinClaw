#!/usr/bin/env python3
"""
基金经理在管基金
查询基金经理管理的所有基金
"""

import akshare as ak
import pandas as pd
import argparse

def get_manager_funds(name):
    """获取基金经理在管基金"""
    try:
        # 获取基金经理管理的基金列表
        df = ak.fund_manager_em()
        
        # 筛选指定基金经理
        funds = df[df['姓名'] == name]
        
        if funds.empty:
            print(f"未找到基金经理 {name} 的在管基金")
            return
        
        print("=" * 90)
        print(f"{name} 在管基金列表")
        print("=" * 90)
        
        print(f"{'基金代码':<12} {'基金名称':<25} {'任职日期':<12} {'任期回报%':<12}")
        print("-" * 90)
        
        for _, row in funds.iterrows():
            print(f"{row.get('基金代码', '--'):<12} {row.get('基金名称', '--')[:25]:<25} "
                  f"{row.get('上任日期', '--'):<12} {row.get('任期回报', '--'):<12}")
        
        print("=" * 90)
        print(f"共管理 {len(funds)} 只基金")
        
    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True, help='基金经理姓名')
    
    args = parser.parse_args()
    get_manager_funds(args.name)
