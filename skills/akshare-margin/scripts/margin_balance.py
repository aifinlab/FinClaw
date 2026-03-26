#!/usr/bin/env python3
"""
沪深两市融资融券余额查询
获取沪深两市整体融资融券余额数据
"""

import pandas as pd
from datetime import datetime
import akshare as ak
import argparse


def get_margin_balance():
    """获取沪深两市融资融券余额"""
    try:
        # 获取融资融券汇总数据
        df = ak.stock_margin_szse()

        if df.empty:
            print("暂无融资融券数据")
            return

        # 显示最新数据
        latest = df.iloc[0]

        print("=" * 60)
        print("沪深两市融资融券余额")
        print("=" * 60)
        print(f"数据日期: 最新")
        print("-" * 60)

        # 深圳市场
        print("\n【深圳市场】")
        print(f"  融资余额: {latest['融资余额']:,.0f} 元")
        print(f"  融券余额: {latest['融券余额']:,.0f} 元")
        print(f"  融资融券余额: {latest['融资融券余额']:,.0f} 元")

        # 获取上海市场数据
        df_sh = ak.stock_margin_sse()
        if not df_sh.empty:
            latest_sh = df_sh.iloc[0]
            print("\n【上海市场】")
            print(f"  融资余额: {latest_sh['融资余额']:,.0f} 元")
            print(f"  融券余额: {latest_sh['融券余量金额']:,.0f} 元")
            print(f"  融资融券余额: {latest_sh['融资融券余额']:,.0f} 元")

            # 合计
            total_margin = latest['融资融券余额'] + latest_sh['融资融券余额']
            print("\n【两市合计】")
            print(
                f"  融资融券总余额: {
                    total_margin:,.0f} 元 ({
            total_margin /
                    1e12:.2f} 万亿元)")

        print("=" * 60)

    except Exception as e:
        print(f"获取数据失败: {e}")


def get_margin_trend(days=30):
    """获取融资融券余额趋势"""
    try:
        # 深圳市场
        df_sz = ak.stock_margin_szse()
        df_sh = ak.stock_margin_sse()

        if df_sz.empty or df_sh.empty:
            print("暂无趋势数据")
            return

        # 取最近N天
        df_sz = df_sz.head(days)
        df_sh = df_sh.head(days)

        print("\n" + "=" * 60)
        print(f"融资融券余额趋势 (最近{days}天)")
        print("=" * 60)
        print(f"{'序号':<8} {'深圳余额(亿)':<15} {'上海余额(亿)':<15} {'合计(亿)':<15}")
        print("-" * 60)

        for i in range(min(len(df_sz), len(df_sh))):
            sz_balance = df_sz.iloc[i]['融资融券余额']
            sh_balance = df_sh.iloc[i]['融资融券余额']
            total = sz_balance + sh_balance

            print(
                f"{i + 1:<8} {sz_balance:<15.2f} {sh_balance:<15.2f} {total:<15.2f}")

        print("=" * 60)

    except Exception as e:
        print(f"获取趋势数据失败: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='融资融券余额查询')
    parser.add_argument('--trend', action='store_true', help='显示趋势数据')
    parser.add_argument('--days', type=int, default=30, help='趋势天数 (默认30)')

    args = parser.parse_args()

    if args.trend:
        get_margin_trend(args.days)
    else:
        get_margin_balance()
