#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双均线策略回测 - Backtrader
"""

import akshare as ak
import backtrader as bt
import sys


def validate_input(data: dict) -> dict:
    """验证输入参数"""
    if not isinstance(data, dict):
        raise ValueError("输入必须是字典类型")

    required_fields = []  # 添加必填字段
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")

    return data



class SmaStrategy(bt.Strategy):
    """双均线策略"""
    params = (
        ('fast', 5),
        ('slow', 20),
    )

    def __init__(self):
        self.fast_sma = bt.indicators.SMA(period=self.p.fast)
        self.slow_sma = bt.indicators.SMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.sell()

def run_backtest(stock="600519", start="20230101", end="20241231"):
    """运行回测"""
    # 获取数据
    try:
        df = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date=start, end_date=end, adjust="qfq")
        df['date'] = df['日期']
        df['open'] = df['开盘']
        df['high'] = df['最高']
        df['low'] = df['最低']
        df['close'] = df['收盘']
        df['volume'] = df['成交量']
        df.set_index('date', inplace=True)
    except:
        print("获取数据失败")
        return

    # 创建回测引擎
    cerebro = bt.Cerebro()

    # 添加数据
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(SmaStrategy)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 设置佣金
    cerebro.broker.setcommission(commission=0.001)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    # 运行回测
    print(f"初始资金: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    print(f"最终资金: {cerebro.broker.getvalue():.2f}")

    # 输出绩效
    strat = results[0]
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()

    print(f"\n📊 绩效指标:")
    print(f"   夏普比率: {sharpe.get('sharperatio', 'N/A')}")
    print(f"   最大回撤: {drawdown.get('max', 'N/A')}")
    print(f"   年化收益: {returns.get('rnorm100', 'N/A')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        stock = sys.argv[1]
        run_backtest(stock)
    else:
        run_backtest("600519")
