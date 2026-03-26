#!/usr/bin/env python3
"""
概念板块行情
查询指定概念板块的行情
"""

import akshare as ak
import argparse
import pandas as pd


def get_concept_quote(name):
    """获取概念板块行情"""
    try:
        df = ak.stock_board_concept_hist_em(symbol=name, period="daily")

        if df.empty:
            print(f"未找到板块: {name}")
            return

        print("=" * 90)
        print(f"{name} 概念板块行情")
        print("=" * 90)

        # 最新数据
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        change = latest['收盘'] - prev['收盘']
        change_pct = (latest['收盘'] / prev['收盘'] - 1) * 100

        print(f"\n【最新行情】")
        print(f"  日期: {latest['日期']}")
        print(f"  收盘: {latest['收盘']:.2f}")
        print(f"  涨跌: {change:+.2f} ({change_pct:+.2f}%)")
        print(f"  成交量: {latest['成交量'] / 1e8:.2f} 亿")
        print(f"  成交额: {latest['成交额'] / 1e8:.2f} 亿")

        # 近期走势
        print(f"\n【近期走势 (最近10天)】")
        print(f"{'日期':<12} {'收盘':<10} {'涨跌幅%':<10} {'成交额(亿)':<12}")
        print("-" * 60)

        recent = df.tail(10)
        for i in range(len(recent)):
            row = recent.iloc[i]
            if i > 0:
                prev_row = recent.iloc[i - 1]
                day_change = (row['收盘'] / prev_row['收盘'] - 1) * 100
            else:
                day_change = 0

            print(f"{row['日期']:<12} {row['收盘']:<10.2f} "
                    f"{day_change:<10.2f} {row['成交额'] / 1e8:<12.2f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")


def get_concept_stocks(name):
    """获取概念板块成分股"""
    try:
        df = ak.stock_board_concept_cons_em(symbol=name)

        if df.empty:
            print(f"未找到板块: {name}")
            return

        print("=" * 90)
        print(f"{name} 概念板块成分股")
        print("=" * 90)

        print(f"{'代码':<10} {'名称':<12} {'最新价':<10} {'涨跌幅%':<10} {'成交额(万)':<12}")
        print("-" * 90)

        for _, row in df.head(30).iterrows():
            change = row.get('涨跌幅', 0)
            print(f"{row['代码']:<10} {row['名称']:<12} "
                    f"{row.get('最新价', 0):<10.2f} {change:<10.2f} "
                    f"{row.get('成交额', 0) / 1e4:<12.1f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True, help='板块名称')
    parser.add_argument('--stocks', action='store_true', help='显示成分股')

    args = parser.parse_args()

    if args.stocks:
        get_concept_stocks(args.name)
    else:
        get_concept_quote(args.name)
