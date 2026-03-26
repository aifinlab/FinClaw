#!/usr/bin/env python3
"""
机构大宗交易追踪
分析机构专用席位的大宗交易动向
"""

import akshare as ak
import argparse
import pandas as pd

def get_institution_block_trade(days=30):
    """获取机构大宗交易数据"""
    try:
        # 获取大宗交易数据
        df = ak.stock_dzjy_mrtj()

        if df.empty:
            print("暂无大宗交易数据")
            return

        # 筛选机构席位
        inst_buy = df[df['买方营业部'].str.contains('机构专用', na=False)]
        inst_sell = df[df['卖方营业部'].str.contains('机构专用', na=False)]

        print("=" * 90)
        print("机构大宗交易分析")
        print("=" * 90)

        # 机构买入统计
        if not inst_buy.empty:
            print(f"\n【机构买入】")
            print(f"  交易笔数: {len(inst_buy)} 笔")
            print(f"  成交金额: {inst_buy['成交额(万元)'].sum():.1f} 万元")

            print(f"\n  机构买入 TOP10:")
            top_buy = inst_buy.sort_values('成交额(万元)', ascending=False).head(10)
            print(f"  {'代码':<10} {'名称':<12} {'金额(万)':<12} {'折溢价%':<10}")
            print("  " + "-" * 50)
            for _, row in top_buy.iterrows():
                print(f"  {row['证券代码']:<10} {row['证券简称']:<12} "
                      f"{row['成交额(万元)']:<12.1f} {row['折溢价率']:<10.2f}")

        # 机构卖出统计
        if not inst_sell.empty:
            print(f"\n【机构卖出】")
            print(f"  交易笔数: {len(inst_sell)} 笔")
            print(f"  成交金额: {inst_sell['成交额(万元)'].sum():.1f} 万元")

            print(f"\n  机构卖出 TOP10:")
            top_sell = inst_sell.sort_values('成交额(万元)', ascending=False).head(10)
            print(f"  {'代码':<10} {'名称':<12} {'金额(万)':<12} {'折溢价%':<10}")
            print("  " + "-" * 50)
            for _, row in top_sell.iterrows():
                print(f"  {row['证券代码']:<10} {row['证券简称']:<12} "
                      f"{row['成交额(万元)']:<12.1f} {row['折溢价率']:<10.2f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取数据失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='机构大宗交易追踪')
    parser.add_argument('--days', type=int, default=30, help='查询天数')

    args = parser.parse_args()
    get_institution_block_trade(args.days)
