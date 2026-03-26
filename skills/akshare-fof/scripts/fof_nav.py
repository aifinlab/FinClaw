#!/usr/bin/env python3
"""
FOF基金净值查询
查询FOF基金历史净值
"""

import akshare as ak
import argparse
import pandas as pd

def get_fof_nav(code):
    """获取FOF基金净值"""
    try:
        df = ak.fund_fof_info_em()
        fof_info = df[df['基金代码'] == code]

        if fof_info.empty:
            print(f"未找到FOF基金: {code}")
            return

        name = fof_info.iloc[0]['基金简称']

        # 获取净值数据
        nav_df = ak.fund_open_fund_daily_em()
        nav_data = nav_df[nav_df['基金代码'] == code]

        print("=" * 90)
        print(f"{name} ({code}) 净值信息")
        print("=" * 90)

        if not nav_data.empty:
            latest = nav_data.iloc[0]
            print(f"\n【最新净值】")
            print(f"  单位净值: {latest.get('单位净值', '--')}")
            print(f"  累计净值: {latest.get('累计净值', '--')}")
            print(f"  日增长率: {latest.get('日增长率', '--')}%")
            print(f"  日期: {latest.get('日期', '--')}")

        print("\n【基金信息】")
        print(f"  基金类型: {fof_info.iloc[0].get('基金类型', '--')}")
        print(f"  成立日期: {fof_info.iloc[0].get('成立日期', '--')}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='基金代码')

    args = parser.parse_args()
    get_fof_nav(args.code)
