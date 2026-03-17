# 量化策略回测参考指南

## 回测框架

### 完整回测流程

```
数据准备 → 信号生成 → 仓位管理 → 交易执行 → 绩效评估
```

1. **数据准备**: 获取历史K线、财务数据；处理复权、停牌、缺失值
2. **信号生成**: 根据策略规则计算买入/卖出信号
3. **仓位管理**: 确定每只股票的持仓比例，控制风险敞口
4. **交易执行**: 模拟交易过程，扣除交易成本，处理 T+1/涨跌停
5. **绩效评估**: 计算各项绩效指标，与基准对比

### 信号生成模板

```python
import pandas as pd
import numpy as np

def generate_signals(df, strategy_params):
    """
    生成交易信号
    df: 含 open/high/low/close/volume 的 DataFrame
    返回: signal 列 (1=买入, -1=卖出, 0=无操作)
    """
    signals = pd.Series(0, index=df.index)

    # 示例：均线交叉策略
    short_ma = df['close'].rolling(strategy_params['short_window']).mean()
    long_ma = df['close'].rolling(strategy_params['long_window']).mean()

    # 金叉买入
    signals[(short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))] = 1
    # 死叉卖出
    signals[(short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))] = -1

    return signals
```

### 仓位管理模板

```python
def calculate_positions(signals, max_position=0.2, total_capital=1000000):
    """
    等权重仓位管理
    max_position: 单只股票最大仓位比例
    """
    # 简单等权：持有N只股票时，每只 1/N 仓位
    # 但不超过 max_position
    pass
```

### 交易执行模板

```python
def execute_backtest(df, signals, initial_capital=1000000,
                     commission=0.00025, stamp_tax=0.001, slippage=0.001):
    """
    回测执行引擎
    commission: 佣金费率（双向）
    stamp_tax: 印花税（仅卖出）
    slippage: 滑点
    """
    capital = initial_capital
    position = 0  # 持仓股数
    nav = []  # 净值序列
    trades = []  # 交易记录

    for i in range(len(df)):
        price = df['close'].iloc[i]

        if signals.iloc[i] == 1 and position == 0:
            # 买入（T+1：记录买入日，次日才可卖出）
            buy_cost = price * (1 + commission + slippage)
            shares = int(capital * 0.95 / buy_cost / 100) * 100  # 整手
            if shares > 0:
                cost = shares * buy_cost
                capital -= cost
                position = shares
                trades.append({
                    'date': df.index[i], 'action': 'BUY',
                    'price': price, 'shares': shares, 'cost': cost
                })

        elif signals.iloc[i] == -1 and position > 0:
            # 卖出
            sell_price = price * (1 - commission - stamp_tax - slippage)
            revenue = position * sell_price
            capital += revenue
            trades.append({
                'date': df.index[i], 'action': 'SELL',
                'price': price, 'shares': position, 'revenue': revenue
            })
            position = 0

        # 记录当日净值
        total_value = capital + position * price
        nav.append(total_value / initial_capital)

    return pd.Series(nav, index=df.index), trades
```

## 常用绩效指标

### 收益类指标

| 指标 | 公式 | 说明 |
|------|------|------|
| 总收益率 | (NAV_end / NAV_start) - 1 | 整个回测期间的累计收益 |
| 年化收益率 | NAV_end^(252/N) - 1 | N 为交易天数 |
| 超额收益 | 策略年化收益 - 基准年化收益 | 衡量策略附加价值 |
| Alpha | 回归残差项 | CAPM 模型下的超额收益 |

### 风险类指标

| 指标 | 公式 | 说明 |
|------|------|------|
| 年化波动率 | std(daily_return) * sqrt(252) | 收益率的年化标准差 |
| 最大回撤 | max(1 - NAV / NAV_cummax) | 从峰值到谷底的最大跌幅 |
| 最大回撤持续期 | 最大回撤恢复所需交易日数 | 回撤修复速度 |
| 下行波动率 | std(min(daily_return, 0)) * sqrt(252) | 仅计算负收益的波动 |
| Beta | cov(r_strategy, r_benchmark) / var(r_benchmark) | 系统性风险敞口 |
| VaR(95%) | percentile(daily_return, 5%) | 95%置信度下的单日最大损失 |

### 风险调整收益指标

| 指标 | 公式 | 说明 | 参考值 |
|------|------|------|--------|
| 夏普比率 (Sharpe) | (R_ann - R_f) / sigma_ann | 每单位总风险的超额收益 | >1 良好, >2 优秀 |
| Sortino 比率 | (R_ann - R_f) / sigma_down | 每单位下行风险的超额收益 | >1.5 良好 |
| Calmar 比率 | R_ann / MaxDrawdown | 收益与最大回撤之比 | >1 良好 |
| 信息比率 (IR) | alpha / tracking_error | 每单位跟踪误差的超额收益 | >0.5 良好 |

### 交易统计指标

| 指标 | 说明 |
|------|------|
| 胜率 | 盈利交易数 / 总交易数 |
| 盈亏比 | 平均盈利金额 / 平均亏损金额 |
| 平均持仓天数 | 所有交易的平均持仓时长 |
| 最大连续亏损 | 连续亏损交易的最大次数 |
| 换手率 | 年化交易金额 / 平均持仓市值 |

### 绩效指标计算代码

```python
def calculate_metrics(nav_series, benchmark_series, risk_free_rate=0.025):
    """
    计算完整绩效指标
    nav_series: 策略净值序列（初始=1）
    benchmark_series: 基准净值序列（初始=1）
    risk_free_rate: 年化无风险利率
    """
    # 日收益率
    strategy_returns = nav_series.pct_change().dropna()
    benchmark_returns = benchmark_series.pct_change().dropna()
    trading_days = len(strategy_returns)

    # 年化收益率
    ann_return = nav_series.iloc[-1] ** (252 / trading_days) - 1

    # 年化波动率
    ann_vol = strategy_returns.std() * np.sqrt(252)

    # 夏普比率
    sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0

    # 最大回撤
    cummax = nav_series.cummax()
    drawdown = (nav_series - cummax) / cummax
    max_drawdown = abs(drawdown.min())

    # Calmar 比率
    calmar = ann_return / max_drawdown if max_drawdown > 0 else float('inf')

    # Sortino 比率
    downside_returns = strategy_returns[strategy_returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
    sortino = (ann_return - risk_free_rate) / downside_vol if downside_vol > 0 else 0

    return {
        'total_return': nav_series.iloc[-1] - 1,
        'ann_return': ann_return,
        'ann_volatility': ann_vol,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar,
        'sortino_ratio': sortino,
    }
```

## 回测陷阱

### 1. 前视偏差 (Look-Ahead Bias)
- **问题**: 使用了回测时点尚未公布的数据（如用当期财报选股）
- **防范**: 财务数据需用发布日期而非报告期，至少滞后一个季度

### 2. 幸存者偏差 (Survivorship Bias)
- **问题**: 仅用当前上市股票回测，忽略已退市/ST的股票
- **防范**: 使用包含退市股票的全历史数据；标注是否考虑幸存者偏差

### 3. 过拟合 (Overfitting)
- **问题**: 参数过多/过于精细调优，在样本内表现好但样本外失效
- **防范**:
  - 样本内外分离测试（如 70% 训练 + 30% 验证）
  - 减少参数数量
  - 检查策略在不同时期是否稳定
  - 如夏普比率在某些年份骤降，需警惕

### 4. 交易成本忽略
- **问题**: 不考虑佣金/印花税/滑点，导致回测收益虚高
- **防范**: 始终包含完整交易成本计算

### 5. 流动性忽略
- **问题**: 假设任何时候都能以收盘价成交
- **防范**: 小盘股/低流动性股票需考虑冲击成本；涨跌停时无法成交

### 6. 数据质量问题
- **问题**: 未复权、缺失值、错误数据导致结果失真
- **防范**: 使用前复权价格；检查异常值；处理停牌缺失

## A 股特殊考虑

### T+1 交易制度
- 当日买入的股票，次交易日才能卖出
- 回测中必须标记买入日期，卖出信号最早在买入次日执行

### 涨跌停板制度
| 板块 | 涨跌停幅度 |
|------|-----------|
| 主板 | 10% |
| ST/\*ST | 5% |
| 创业板（注册制后） | 20% |
| 科创板 | 20% |
| 北交所 | 30% |

- **涨停**: 以涨停价挂单可能无法买入（封板），回测中应跳过涨停日买入
- **跌停**: 以跌停价挂单可能无法卖出（封板），回测中应跳过跌停日卖出

### 手续费与税费

| 费用 | 费率 | 说明 |
|------|------|------|
| 佣金 | 万2.5（双向） | 单笔不低于5元；买卖双向收取 |
| 印花税 | 千1（卖出） | 仅卖出时收取 |
| 过户费 | 万0.1（双向） | 可忽略不计 |
| 滑点 | 0.1%（估计值） | 实际执行价与预期价的偏差 |

### 停牌处理
- 停牌期间数据用前一交易日收盘价填充
- 停牌期间无法交易（买卖信号延迟至复牌日执行）
- 长期停牌（>30 天）的股票应从标的池中剔除

### 整手交易
- A 股最小交易单位为 100 股（1 手）
- 买入时需按整手计算，可能导致实际仓位与目标仓位有偏差

### 新股/次新股
- 新股上市首日涨跌幅限制不同（注册制不设涨跌幅前5日）
- 次新股波动大、流动性不稳定，回测时需谨慎

## 常用策略类型与参考参数

### 技术面策略
| 策略 | 参数 | 适用场景 |
|------|------|---------|
| 双均线交叉 | 短期5/10日，长期20/60日 | 趋势跟踪 |
| MACD | (12,26,9) | 趋势判断 |
| RSI 超卖反弹 | RSI<30 买入，RSI>70 卖出 | 震荡市 |
| 布林带突破 | (20, 2) | 波动率突破 |
| 海龟策略 | 20日突破买入，10日突破卖出 | 趋势跟踪 |

### 基本面策略
| 策略 | 因子 | 调仓频率 |
|------|------|---------|
| 低 PE 策略 | PE(TTM) 最低 N% | 季度 |
| 高 ROE 策略 | ROE 最高 N% | 季度 |
| PEG 策略 | PEG < 1 | 季度 |
| 高股息策略 | 股息率最高 N% | 年度 |
| 多因子打分 | PE+PB+ROE+增速加权 | 月度 |

### 量价策略
| 策略 | 逻辑 | 调仓频率 |
|------|------|---------|
| 动量策略 | 买入近N日涨幅前K只 | 月度 |
| 反转策略 | 买入近N日跌幅前K只 | 月度 |
| 量价齐升 | 放量突破前高 | 事件驱动 |
