#!/usr/bin/env python3
"""
个股大宗交易查询
查询指定股票的大宗交易历史
"""

import akshare as ak
import argparse
import pandas as pd

def get_stock_block_trade(code):
    """获取个股大宗交易"""
    try:
        df = ak.stock_dzjy_mrmx(symbol=code)

        if df.empty:
            print(f"未找到 {code} 的大宗交易数据")
            return

        name = df['证券简称'].iloc[0]

        print("=" * 90)
        print(f"{name} ({code}) 大宗交易历史")
        print("=" * 90)

        # 统计
        total_count = len(df)
        total_volume = df['成交量(万股)'].sum()
        total_amount = df['成交额(万元)'].sum()
        avg_premium = df['折溢价率'].mean()

        print(f"\n【交易统计】")
        print(f"  交易次数: {total_count} 次")
        print(f"  累计成交: {total_volume:.2f} 万股")
        print(f"  累计金额: {total_amount:.1f} 万元")
        print(f"  平均折溢价: {avg_premium:.2f}%")

        # 明细
        print(f"\n【交易明细】")
        print(f"{'日期':<12} {'成交价':<10} {'成交量(万股)':<12} {'成交额(万)':<12} {'折溢价%':<10}")
        print("-" * 90)

        for _, row in df.iterrows():
            print(f"{row['交易日期']:<12} {row['成交价']:<10.2f} "
                  f"{row['成交量(万股)']:<12.2f} {row['成交额(万元)']:<12.1f} "
                  f"{row['折溢价率']:<10.2f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='股票代码')

    args = parser.parse_args()
    get_stock_block_trade(args.code)
