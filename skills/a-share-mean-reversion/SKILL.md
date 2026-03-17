---
name: a-share-mean-reversion
description: A股均值回归策略/超跌反弹分析。当用户说"均值回归"、"mean reversion"、"超跌反弹"、"偏离均值"、"回归"、"XX跌太多了会反弹吗"、"布林带策略"、"超买超卖"时触发。基于 cn-stock-data 获取K线数据，分析价格/估值偏离程度，构建均值回归交易策略。支持研报风格（formal）和快速分析风格（brief）。
---

# A股均值回归策略

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow

### Step 1: 选择回归基准
- **价格均值回归**：均线（MA20/MA60/MA120）作为基准
- **估值均值回归**：PE/PB 历史中位数作为基准
- **行业相对回归**：个股 vs 行业指数的相对强弱

### Step 2: 计算偏离度
1. 价格偏离度 = (Price - MA) / MA × 100%
2. 估值偏离度 = (PE - PE_median) / PE_std
3. Z-score 标准化

### Step 3: 半衰期估计
- 基于 Ornstein-Uhlenbeck 模型：dS = θ(μ-S)dt + σdW
- 半衰期 = ln(2) / θ
- 回归 ΔS = a + b×S_{t-1}，半衰期 = -ln(2)/b
- 半衰期越短，均值回归越快

### Step 4: 交易信号
- 超卖入场：Z-score < -2（偏离均值 2 个标准差）
- 超买入场（做空/减仓）：Z-score > +2
- 退出：Z-score 回归至 ±0.5 以内

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 偏离分析 | 多基准偏离度+历史分布 | 当前偏离度 |
| 半衰期 | OU 模型+Hurst 指数 | 预计回归天数 |
| 回测 | 完整绩效 | 胜率+收益 |

默认风格：brief。

## 关键规则
1. 均值回归前提是"均值存在"——趋势行情中均值会漂移
2. Hurst 指数 < 0.5 表示均值回归特性，> 0.5 表示趋势特性
3. A 股短期（1-4 周）有显著反转效应，是均值回归策略的基础
4. 需区分"超跌反弹"和"趋势延续"——结合基本面判断
5. 涨跌停限制可能延长回归时间
