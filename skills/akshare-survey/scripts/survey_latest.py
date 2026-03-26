#!/usr/bin/env python3
"""
最新机构调研查询
获取最新机构调研记录
"""

import akshare as ak
import argparse
import pandas as pd

def get_latest_survey(limit=30):
    """获取最新机构调研"""
    try:
        df = ak.stock_jgdy_detail_em()

        if df.empty:
            print("暂无调研数据")
            return

        print("=" * 90)
        print(f"最新机构调研 TOP{limit}")
        print("=" * 90)

        print(f"{'代码':<10} {'名称':<12} {'调研日期':<12} {'机构数量':<10} {'接待方式':<15}")
        print("-" * 90)

        for _, row in df.head(limit).iterrows():
            print(f"{row['股票代码']:<10} {row['股票简称']:<12} "
                  f"{row['调研日期']:<12} {row['机构数量']:<10} "
                  f"{row['接待方式']:<15}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")

def get_stock_survey(code):
    """获取个股调研记录"""
    try:
        df = ak.stock_jgdy_detail_em()
        stock_df = df[df['股票代码'] == code]

        if stock_df.empty:
            print(f"未找到 {code} 的调研记录")
            return

        name = stock_df.iloc[0]['股票简称']

        print("=" * 90)
        print(f"{name} ({code}) 机构调研记录")
        print("=" * 90)

        for _, row in stock_df.head(10).iterrows():
            print(f"\n【{row['调研日期']}】")
            print(f"  机构数量: {row['机构数量']}")
            print(f"  接待方式: {row['接待方式']}")
            print(f"  调研机构: {row['调研机构'][:80]}...")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=30, help='数量')
    parser.add_argument('--code', type=str, help='股票代码')

    args = parser.parse_args()

    if args.code:
        get_stock_survey(args.code)
    else:
        get_latest_survey(args.limit)
