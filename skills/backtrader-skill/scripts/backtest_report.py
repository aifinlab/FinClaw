#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测绩效报告 - Backtrader
"""

import akshare as ak
import backtrader as bt

def generate_report():
    """生成回测报告模板"""
    print("=" * 80)
    print("📊 回测绩效报告模板")
    print("=" * 80)

    print("""
📈 绩效指标说明:

1. 收益率指标
   - 总收益率: 策略整个回测期的总收益
   - 年化收益率: 折算到每年的收益率
   - 超额收益: 相对基准的收益

2. 风险指标
   - 夏普比率: 风险调整后的收益，>1优秀，>2卓越
   - 最大回撤: 最大亏损幅度，越小越好
   - 波动率: 收益的波动程度

3. 交易指标
   - 胜率: 盈利交易占比
   - 盈亏比: 平均盈利/平均亏损
   - 交易次数: 总交易次数

4. 其他指标
   - Calmar比率: 年化收益/最大回撤
   - Sortino比率: 下行风险调整收益
   - Omega比率: 收益分布的上下尾比率

💡 使用方法:
   python backtest_sma.py <股票代码>
   python backtest_macd.py <股票代码>
   python backtest_boll.py <股票代码>
""")

    print("=" * 80)

if __name__ == "__main__":
    generate_report()
