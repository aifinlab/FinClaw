#!/usr/bin/env python3
"""
基金回测
回测基金历史表现
"""

import akshare as ak
import pandas as pd
import argparse
from datetime import datetime

def backtest_fund(code, start_date, end_date):
    """回测基金"""
    try:
        # 获取基金历史净值
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        
        if df.empty:
            print(f"未找到基金 {code} 的历史数据")
            return
        
        # 筛选日期范围
        df['净值日期'] = pd.to_datetime(df['净值日期'])
        mask = (df['净值日期'] >= start_date) & (df['净值日期'] <= end_date)
        df = df[mask]
        
        if df.empty:
            print("指定日期范围内无数据")
            return
        
        # 计算收益
        start_nav = df['单位净值'].iloc[-1]
        end_nav = df['单位净值'].iloc[0]
        
        total_return = (end_nav / start_nav - 1) * 100
        
        # 计算年化收益
        days = (df['净值日期'].iloc[0] - df['净值日期'].iloc[-1]).days
        if days > 0:
            annual_return = ((end_nav / start_nav) ** (365.25 / days) - 1) * 100
        else:
            annual_return = 0
        
        # 计算最大回撤
        df_sorted = df.sort_values('净值日期')
        df_sorted['cummax'] = df_sorted['单位净值'].cummax()
        df_sorted['drawdown'] = (df_sorted['单位净值'] - df_sorted['cummax']) / df_sorted['cummax'] * 100
        max_drawdown = df_sorted['drawdown'].min()
        
        # 计算波动率
        df_sorted['daily_return'] = df_sorted['单位净值'].pct_change()
        volatility = df_sorted['daily_return'].std() * (252 ** 0.5) * 100
        
        print("=" * 70)
        print(f"基金回测结果 ({code})")
        print(f"回测区间: {start_date} 至 {end_date}")
        print("=" * 70)
        
        print(f"\n【回测指标】")
        print(f"  期初净值: {start_nav:.4f}")
        print(f"  期末净值: {end_nav:.4f}")
        print(f"  总收益率: {total_return:.2f}%")
        print(f"  年化收益: {annual_return:.2f}%")
        print(f"  最大回撤: {max_drawdown:.2f}%")
        print(f"  波动率: {volatility:.2f}%")
        
        if max_drawdown != 0:
            calmar = annual_return / abs(max_drawdown)
            print(f"  卡玛比率: {calmar:.2f}")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"回测失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True, help='基金代码')
    parser.add_argument('--start', type=str, required=True, help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='结束日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    backtest_fund(args.code, args.start, args.end)
