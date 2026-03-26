#!/usr/bin/env python3
"""
高管增减持查询
查询最新高管持股变动
"""

import akshare as ak
import argparse
import pandas as pd


def get_executive_change(limit=30):
    """获取高管增减持"""
    try:
        df = ak.stock_ggcg_em()

        if df.empty:
            print("暂无数据")
            return

        print("=" * 90)
        print(f"最新高管持股变动 TOP{limit}")
        print("=" * 90)

        print(f"{'代码':<10} {'名称':<12} {'高管姓名':<10} {'变动股数':<12} {'变动方向':<10} {'变动日期':<12}")
        print("-" * 90)

        for _, row in df.head(limit).iterrows():
            direction = "增持" if "增持" in str(row.get('变动方向', '')) else "减持"
            print(f"{row['股票代码']:<10} {row['股票简称']:<12} "
                    f"{row.get('高管姓名', '--'):<10} {row.get('变动股数', 0):<12.0f} "
                    f"{direction:<10} {row.get('变动日期', '--'):<12}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")


def get_stock_executive(code):
    """获取个股高管变动"""
    try:
        df = ak.stock_ggcg_em()
        stock_df = df[df['股票代码'] == code]

        if stock_df.empty:
            print(f"未找到 {code} 的高管变动记录")
            return

        name = stock_df.iloc[0]['股票简称']

        print("=" * 90)
        print(f"{name} ({code}) 高管持股变动")
        print("=" * 90)

        for _, row in stock_df.head(10).iterrows():
            print(f"\n【{row.get('高管姓名', '--')}】")
            print(f"  职务: {row.get('职务', '--')}")
            print(f"  变动方向: {row.get('变动方向', '--')}")
            print(f"  变动股数: {row.get('变动股数', 0):.0f}")
            print(f"  变动日期: {row.get('变动日期', '--')}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=30, help='数量')
    parser.add_argument('--code', type=str, help='股票代码')

    args = parser.parse_args()

    if args.code:
        get_stock_executive(args.code)
    else:
        get_executive_change(args.limit)
