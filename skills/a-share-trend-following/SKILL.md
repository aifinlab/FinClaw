---
name: a-share-trend-following
description: A股趋势跟踪策略/趋势强度分析。当用户说"趋势跟踪"、"trend following"、"趋势交易"、"顺势"、"趋势强度"、"ADX"、"均线策略"、"海龟策略"、"突破策略"时触发。基于 cn-stock-data 获取K线数据，构建趋势跟踪策略，分析趋势强度和方向。支持研报风格（formal）和快速分析风格（brief）。
---

# A股趋势跟踪策略 (a-share-trend-following)

## 数据获取

通过 cn-stock-data skill 获取K线数据：
- 日K线：至少 120 个交易日（均线计算需要足够回溯期）
- 周K线：可选，用于多周期共振确认
- 调用方式：`cn-stock-data` kline 接口，获取 OHLCV 数据

## 分析流程

### Step 1: 获取K线数据
- 使用 cn-stock-data 获取目标股票日K线（默认 250 日）
- 保存为 JSON 供 `scripts/trend_follower.py` 使用

### Step 2: 计算趋势指标
运行脚本：
```bash
python scripts/trend_follower.py --data kline.json --method all --fast 20 --slow 60
```

核心指标体系：
| 指标 | 用途 | 默认参数 |
|------|------|---------|
| SMA/EMA 交叉 | 趋势方向判定 | fast=20, slow=60 |
| ADX/DMI | 趋势强度量化 | period=14 |
| Donchian Channel | 突破信号 | period=20 |
| ATR Trailing Stop | 动态止损 | period=14, multiplier=2.0 |

### Step 3: 趋势状态判定
根据指标综合判定当前趋势regime：
- **强上升趋势**: ADX>25 且 +DI>-DI 且价格在均线上方
- **弱上升趋势**: 价格在均线上方但 ADX<25
- **震荡/无趋势**: ADX<20，均线缠绕
- **弱下降趋势**: 价格在均线下方但 ADX<25
- **强下降趋势**: ADX>25 且 -DI>+DI 且价格在均线下方

### Step 4: 生成交易信号与回测
- 策略可选：`ma_cross`（均线交叉）、`donchian`（突破）、`turtle`（海龟）、`all`（综合）
- 回测指标：累计收益、年化收益、Sharpe ratio、最大回撤、胜率、盈亏比、Profit Factor

### Step 5: 输出结果

## A股特殊考量
- **T+1 制度**: 买入当日不可卖出，信号需延迟一日执行
- **涨跌停板**: 涨停无法买入 / 跌停无法卖出，需检测涨跌停状态
- **停牌缺口**: 停牌后复牌可能跳空，ATR 止损需特殊处理
- **印花税**: 卖出 0.05%（2024年起），佣金双边 0.025%

## 输出风格

### formal（研报风格）
```
## 趋势跟踪分析报告：{股票名称}({代码})
### 一、趋势状态总览
### 二、趋势指标详情
### 三、交易信号与策略
### 四、回测绩效
### 五、风险提示与操作建议
```

### brief（快速分析风格）
```
{股票名称} 趋势跟踪速览
趋势状态: 强上升 | ADX={value}
当前信号: 持有/买入/卖出/观望
关键价位: 止损={x} 止盈={y}
近期绩效: 胜率={w}% Sharpe={s}
```

## 注意事项
- 趋势策略在震荡市中容易产生频繁假信号（whipsaw），需结合 ADX 过滤
- 单一策略不构成投资建议，应结合基本面和市场环境综合判断
- 回测结果不代表未来表现，注意过拟合风险
