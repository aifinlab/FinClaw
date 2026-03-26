#!/usr/bin/env python3
"""
REITs行情查询
查询REITs实时行情
"""

import akshare as ak
import argparse
import pandas as pd


def get_reits_quote():
    """获取REITs行情"""
    try:
        df = ak.reit_stock_js()

        if df.empty:
            print("暂无数据")
            return

        print("=" * 90)
        print("REITs实时行情")
        print("=" * 90)

        # 按涨跌幅排序
        df_sorted = df.sort_values('涨跌幅', ascending=False)

        print(f"{'代码':<10} {'名称':<18} {'最新价':<10} {'涨跌幅%':<10} {'成交额(万)':<12}")
        print("-" * 90)

        for _, row in df_sorted.head(30).iterrows():
            name = str(row.get('名称', '--'))[:18]
            print(f"{row.get('代码', '--'):<10} {name:<18} "
                    f"{row.get('最新价', 0):<10.3f} {row.get('涨跌幅', 0):<10.2f} "
                    f"{row.get('成交额', 0)/1e4:<12.2f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")


if __name__ == "__main__":
    get_reits_quote()
