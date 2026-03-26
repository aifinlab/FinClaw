#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例PE-PB-ROE多因子策略
用于测试china-backtest-expert
"""
import numpy as np
import pandas as pd

def generate_sample_backtest_data(n_days=1000, seed=42):
    """生成示例回测数据"""
    np.random.seed(seed)

    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='B')

    # 生成价格数据
    returns = np.random.normal(0.0005, 0.02, n_days)  # 正收益，适度波动
    prices = 100 * (1 + returns).cumprod()

    # 生成交易记录
    trades = []
    for i in range(0, n_days, 20):  # 每20天交易一次
        if i + 20 < n_days:
            trades.append({
                'date': dates[i],
                'action': 'buy',
                'price': prices[i],
                'shares': 100
            })
            trades.append({
                'date': dates[i+10],
                'action': 'sell',
                'price': prices[i+10],
                'shares': 100,
                'holding_days': 10
            })

    df = pd.DataFrame({
        'date': dates,
        'close': prices,
        'open': prices * (1 + np.random.normal(0, 0.001, n_days)),
        'high': prices * (1 + abs(np.random.normal(0, 0.01, n_days))),
        'low': prices * (1 - abs(np.random.normal(0, 0.01, n_days))),
        'volume': np.random.randint(1000000, 10000000, n_days),
        'return': returns
    })

    trades_df = pd.DataFrame(trades)

    return df, trades_df


if __name__ == '__main__':
    # 生成测试数据
    data, trades = generate_sample_backtest_data()
    data.to_csv('sample_backtest_data.csv', index=False)
    trades.to_csv('sample_trades.csv', index=False)
    print("示例数据已生成: sample_backtest_data.csv, sample_trades.csv")
