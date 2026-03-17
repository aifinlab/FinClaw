---
name: a-share-drawdown-analysis
description: A股回撤分析/最大回撤量化/回撤统计。当用户说"回撤"、"drawdown"、"最大回撤"、"回撤分析"、"回撤统计"、"历史回撤"、"水下曲线"、"亏了多少"、"从高点跌了多少"、"回撤修复"、"回撤天数"时触发。MUST USE when user asks about drawdown metrics, max drawdown calculation, or historical drawdown analysis for stocks/indices/portfolios. 基于 cn-stock-data 获取K线数据，量化分析历史回撤特征（最大回撤、回撤持续期、回撤修复时间、水下曲线）。支持研报风格（formal）和快速分析风格（brief）。
---

# A股回撤分析/最大回撤量化

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取K线数据
获取足够长的历史数据（建议 2 年以上）。

### Step 2: 计算回撤序列
- 滚动最高价 = max(close[:t])
- 回撤 = (close - 滚动最高价) / 滚动最高价 × 100%
- 最大回撤 = min(回撤序列)

### Step 3: 回撤事件分析
- 识别所有回撤 > 10% 的事件
- 每次回撤的起点/终点/最低点/持续天数/恢复天数
- 回撤期间成交量变化

### Step 4: 回撤统计
- 平均回撤深度/持续时间/恢复时间
- 回撤频率（年均几次 > 5%/10%/20%）
- 与大盘回撤的对比（β调整后回撤）

### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 回撤序列 | 完整回撤图表+事件表 | 最大回撤值 |
| 统计分析 | 回撤分布+恢复时间 | 关键统计 |
| 风险评估 | 压力测试情景 | 当前回撤状态 |

默认风格：brief。

## 关键规则
1. 最大回撤是衡量风险的核心指标之一
2. 恢复时间往往比回撤深度更影响投资者体验
3. A 股历史上大盘级别回撤：2008(-72%)、2015(-49%)、2018(-31%)
4. 个股回撤通常远大于指数回撤
5. 回撤期间的成交量放大通常意味着恐慌性抛售
