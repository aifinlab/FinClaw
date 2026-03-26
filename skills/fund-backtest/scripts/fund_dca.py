#!/usr/bin/env python3
"""
定投收益计算
计算基金定投收益
"""

from datetime import datetime, timedelta
import akshare as ak
import argparse
import pandas as pd

def calculate_dca(code, monthly_amount=1000, years=3):
    """计算定投收益"""
    try:
        # 获取基金历史净值
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

        if df.empty:
            print(f"未找到基金 {code} 的历史数据")
            return

        df['净值日期'] = pd.to_datetime(df['净值日期'])
        df = df.sort_values('净值日期')

        # 模拟定投（每月1日买入）
        end_date = df['净值日期'].max()
        start_date = end_date - timedelta(days=365*years)

        # 获取定投日期（每月第一个交易日）
        df_period = df[df['净值日期'] >= start_date]
        df_period['年月'] = df_period['净值日期'].dt.to_period('M')

        # 每月第一个交易日
        dca_dates = df_period.groupby('年月')['净值日期'].min()

        total_shares = 0
        total_invested = 0

        for date in dca_dates:
            nav = df_period[df_period['净值日期'] == date]['单位净值'].iloc[0]
            shares = monthly_amount / nav
            total_shares += shares
            total_invested += monthly_amount

        # 计算期末市值
        final_nav = df['单位净值'].iloc[-1]
        final_value = total_shares * final_nav
        total_return = final_value - total_invested
        return_rate = (final_value / total_invested - 1) * 100

        print("=" * 70)
        print(f"定投收益计算 ({code})")
        print("=" * 70)

        print(f"\n【定投计划】")
        print(f"  定投金额: {monthly_amount} 元/月")
        print(f"  定投周期: {years} 年 ({len(dca_dates)} 个月)")
        print(f"  累计投入: {total_invested} 元")

        print(f"\n【收益情况】")
        print(f"  持有份额: {total_shares:.2f} 份")
        print(f"  期末净值: {final_nav:.4f}")
        print(f"  期末市值: {final_value:.2f} 元")
        print(f"  总收益: {total_return:.2f} 元")
        print(f"  收益率: {return_rate:.2f}%")

        print("=" * 70)

    except Exception as e:
        print(f"计算失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='基金代码')
    parser.add_argument('--amount', type=float, default=1000, help='每月定投金额')
    parser.add_argument('--years', type=int, default=3, help='定投年数')

    args = parser.parse_args()
    calculate_dca(args.code, args.amount, args.years)
