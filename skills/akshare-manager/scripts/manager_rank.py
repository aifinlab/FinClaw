#!/usr/bin/env python3
"""
基金经理业绩排行
查询基金经理业绩排行
"""

import akshare as ak
import argparse
import pandas as pd

def get_manager_rank(period='1y'):
    """获取基金经理排行"""
    try:
        df = ak.fund_manager_rank_em()

        if df.empty:
            print("暂无数据")
            return

        # 根据周期排序
        period_map = {
            '1y': '近1年收益',
            '2y': '近2年收益',
            '3y': '近3年收益',
            '5y': '近5年收益'
        }

        sort_col = period_map.get(period, '近1年收益')

        print("=" * 90)
        print(f"基金经理业绩排行 ({sort_col})")
        print("=" * 90)

        df_sorted = df.sort_values(sort_col, ascending=False)

        print(f"{'排名':<6} {'姓名':<10} {'在管基金':<10} {'任期':<10} {'{sort_col}':<12}")
        print("-" * 70)

        for i, (_, row) in enumerate(df_sorted.head(30).iterrows(), 1):
            print(f"{i:<6} {row['姓名']:<10} {row.get('在管基金', '--'):<10} "
                  f"{row.get('任职年限', '--'):<10} {row.get(sort_col, '--'):<12}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")

def get_manager_detail(name):
    """获取基金经理详情"""
    try:
        df = ak.fund_manager_rank_em()
        manager = df[df['姓名'] == name]

        if manager.empty:
            print(f"未找到基金经理: {name}")
            return

        print("=" * 70)
        print(f"基金经理详情 - {name}")
        print("=" * 70)

        row = manager.iloc[0]
        print(f"\n【基本信息】")
        print(f"  在管基金: {row.get('在管基金', '--')} 只")
        print(f"  任职年限: {row.get('任职年限', '--')} 年")
        print(f"  现任公司: {row.get('现任公司', '--')}")

        print(f"\n【业绩表现】")
        print(f"  近1年收益: {row.get('近1年收益', '--')}")
        print(f"  近2年收益: {row.get('近2年收益', '--')}")
        print(f"  近3年收益: {row.get('近3年收益', '--')}")
        print(f"  近5年收益: {row.get('近5年收益', '--')}")

        print("=" * 70)

    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--period', type=str, default='1y', choices=['1y', '2y', '3y', '5y'])
    parser.add_argument('--name', type=str, help='基金经理姓名')

    args = parser.parse_args()

    if args.name:
        get_manager_detail(args.name)
    else:
        get_manager_rank(args.period)
