#!/usr/bin/env python3
"""
每日大宗交易数据查询
获取当日大宗交易明细
"""

from datetime import datetime
import akshare as ak
import argparse
import pandas as pd

def get_daily_block_trade(date=None):
    """
    获取每日大宗交易数据

    Args:
        date: 日期格式 YYYY-MM-DD，默认最新
    """
    try:
        # 获取大宗交易数据
        if date:
            df = ak.stock_dzjy_mrtj(start_date=date, end_date=date)
        else:
            df = ak.stock_dzjy_mrtj()

        if df.empty:
            print("暂无大宗交易数据")
            return

        print("=" * 90)
        print("大宗交易日报")
        print(f"数据日期: {df['交易日期'].iloc[0] if '交易日期' in df.columns else '最新'}")
        print("=" * 90)

        # 统计
        total_count = len(df)
        total_volume = df['成交量(万股)'].sum()
        total_amount = df['成交额(万元)'].sum()

        print(f"\n【市场统计】")
        print(f"  交易笔数: {total_count} 笔")
        print(f"  成交总量: {total_volume:.2f} 万股")
        print(f"  成交总额: {total_amount:.2f} 万元 ({total_amount/1e4:.2f} 亿元)")
        print(f"  平均单笔: {total_amount/total_count:.2f} 万元")

        # 折溢价分布
        premium_count = len(df[df['折溢价率'] > 0])
        discount_count = len(df[df['折溢价率'] < 0])
        flat_count = len(df[df['折溢价率'] == 0])

        print(f"\n【折溢价分布】")
        print(f"  溢价成交: {premium_count} 笔 ({premium_count/total_count*100:.1f}%)")
        print(f"  平价成交: {flat_count} 笔 ({flat_count/total_count*100:.1f}%)")
        print(f"  折价成交: {discount_count} 笔 ({discount_count/total_count*100:.1f}%)")

        # 成交额排行
        print(f"\n【成交额 TOP20】")
        df_sorted = df.sort_values('成交额(万元)', ascending=False).head(20)

        print(f"{'代码':<10} {'名称':<12} {'成交额(万)':<12} {'成交量(万股)':<12} {'折溢价率%':<10}")
        print("-" * 90)

        for _, row in df_sorted.iterrows():
            print(f"{row['证券代码']:<10} {row['证券简称']:<12} "
                  f"{row['成交额(万元)']:<12.1f} {row['成交量(万股)']:<12.2f} "
                  f"{row['折溢价率']:<10.2f}")

        print("=" * 90)

    except Exception as e:
        print(f"获取数据失败: {e}")

def get_block_detail(code, start_date=None, end_date=None):
    """获取个股大宗交易明细"""
    try:
        # 获取个股大宗交易数据
        df = ak.stock_dzjy_mrmx(symbol=code)

        if df.empty:
            print(f"未找到股票 {code} 的大宗交易数据")
            return

        stock_name = df['证券简称'].iloc[0] if '证券简称' in df.columns else '未知'

        print("=" * 90)
        print(f"{stock_name} ({code}) 大宗交易明细")
        print("=" * 90)

        print(f"\n{'日期':<12} {'成交价':<10} {'成交量(万股)':<12} {'成交额(万)':<12} {'折溢价%':<10}")
        print("-" * 90)

        for _, row in df.head(30).iterrows():
            print(f"{row['交易日期']:<12} {row['成交价']:<10.2f} "
                  f"{row['成交量(万股)']:<12.2f} {row['成交额(万元)']:<12.1f} "
                  f"{row['折溢价率']:<10.2f}")

        # 统计
        total_volume = df['成交量(万股)'].sum()
        total_amount = df['成交额(万元)'].sum()
        avg_premium = df['折溢价率'].mean()

        print("-" * 90)
        print(f"{'合计':<12} {'':<10} {total_volume:<12.2f} {total_amount:<12.1f} {avg_premium:<10.2f}")
        print("=" * 90)

    except Exception as e:
        print(f"获取明细失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='大宗交易数据查询')
    parser.add_argument('--date', type=str, help='日期 (格式: YYYY-MM-DD)')
    parser.add_argument('--code', type=str, help='股票代码')

    args = parser.parse_args()

    if args.code:
        get_block_detail(args.code, args.date)
    else:
        get_daily_block_trade(args.date)
