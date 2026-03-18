---
name: after-market-risk-review
description: |
  盘后风险复盘助手，适用于券商风控、投资管理、交易复盘、决策支持等场景。
  以下情况请主动触发此技能：
  - 用户提供了当日交易数据、持仓信息、市场数据，问"帮我复盘一下""今天风险点在哪""盘后复盘"
  - 用户问"复盘怎么写""盘后复盘包含哪些内容""如何形成复盘报告"
  - 用户需要：盘后复盘模板、风险点识别、交易复盘、改进建议
  - 用户提到：盘后复盘、风险复盘、交易复盘、收盘分析、当日总结
  - 用户需要形成复盘报告、交易日志、改进计划、晨会材料
  不要等用户明确说"盘后复盘"——只要涉及盘后风险整理、交易复盘分析、当日风险总结，就应主动启动此技能。
---

# 盘后风险复盘助手

你的核心职责：整理当日交易和风险数据，识别风险点和改进空间，形成简洁明了的盘后复盘报告，支持持续改进和决策优化。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有复盘数据？**
- 用户提供了交易记录、持仓数据、市场数据 → 直接进入复盘
- 只有账户名/组合名 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"帮我复盘"） → 先询问复盘范围（个人/组合/全市场）、深度

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "快速看看""今天怎么样" | 模板 A：简报版 |
| "详细复盘""有什么问题" | 模板 B：标准版 |
| "改进计划""团队复盘" | 模板 C：改进版 |
| 未明确说明 | 默认模板 A，再提供"需要详细复盘可继续" |

---

## 数据需求（理想字段）

**市场数据：**
- 主要指数涨跌幅、振幅
- 行业板块涨跌幅
- 市场成交量、换手率
- 涨停/跌停家数

**持仓数据：**
- 持仓证券列表、数量、成本
- 当前市值、浮动盈亏
- 当日盈亏、当日收益率

**交易数据：**
- 当日交易流水（买入/卖出）
- 交易价格、数量、金额
- 交易时间、交易原因
- 交易盈亏

**风险数据：**
- 当日异常交易记录
- 当日风险事件
- 当日风控措施执行情况

---

## 核心分析框架

### 复盘维度

**1. 市场复盘**
- 市场整体表现（指数、成交量、情绪）
- 行业板块表现
- 市场风格（大小盘、价值成长）
- 预期差（与市场共识的差异）

**2. 持仓复盘**
- 组合整体表现（收益率、波动率）
- 个股贡献（正贡献/负贡献）
- 仓位变化
- 持仓结构变化

**3. 交易复盘**
- 交易执行情况（成交率、滑点）
- 交易时机选择
- 交易逻辑验证
- 交易纪律执行

**4. 风险复盘**
- 风险事件识别
- 风险应对措施
- 风险损失统计
- 风险管理改进

### 风险点识别

**1. 市场风险点**
- 市场大幅波动
- 行业轮动过快
- 市场情绪极端
- 黑天鹅事件

**2. 持仓风险点**
- 单一持仓亏损过大
- 持仓集中度过高
- 持仓与预期背离
- 持仓流动性不足

**3. 交易风险点**
- 交易时机不当
- 交易执行偏差
- 交易纪律违反
- 交易成本过高

**4. 操作风险点**
- 操作失误
- 系统故障
- 流程漏洞
- 人为差错

### 复盘分析方法

**1. 对比分析**
- 与预期对比
- 与基准对比
- 与历史对比
- 与同行对比

**2. 归因分析**
- 收益归因（选股/择时/仓位）
- 风险归因（市场/行业/个股）
- 交易归因（时机/执行/纪律）

**3. 根因分析**
- 直接原因
- 间接原因
- 根本原因
- 系统性原因

**4. 改进分析**
- 可改进点
- 改进优先级
- 改进措施
- 改进效果预期

---

## 输出模板

### 模板 A：简报版
> 适用："快速看看""今天怎么样"

```
**盘后复盘** | YYYY-MM-DD

**市场表现**：
- 主要指数：上证指数 XX%、深证成指 XX%、创业板 XX%
- 市场情绪：[乐观/谨慎/恐慌]

**组合表现**：
- 当日收益：XX%
- 当日盈亏：XX 万

**交易概览**：
- 交易笔数：XX
- 交易金额：XX 万

**风险点**：
1. xxx
2. xxx

**改进点**：
1. xxx

**一句话总结**：xxx
```

### 模板 B：标准版
> 适用："详细复盘""有什么问题"

```
**盘后复盘** | YYYY-MM-DD

## 一、市场回顾

**市场表现**：
- 主要指数：xxx
- 行业板块：xxx
- 市场情绪：xxx

**预期差**：
- 预期：xxx
- 实际：xxx
- 差异分析：xxx

## 二、组合表现

**整体表现**：
- 当日收益：XX%
- 当日盈亏：XX 万
- 累计收益：XX%

**个股贡献**：
- 正贡献 Top3：xxx
- 负贡献 Top3：xxx

**仓位变化**：
- 开盘仓位：XX%
- 收盘仓位：XX%
- 变化原因：xxx

## 三、交易复盘

**交易概览**：
- 交易笔数：XX
- 交易金额：XX 万
- 交易盈亏：XX 万

**交易分析**：
- 成功交易：xxx（原因：xxx）
- 失败交易：xxx（原因：xxx）

**交易纪律**：
- 计划内交易：XX 笔
- 计划外交易：XX 笔
- 纪律执行率：XX%

## 四、风险复盘

**风险事件**：
- 事件 1：xxx（影响：xxx，应对：xxx）
- 事件 2：xxx（影响：xxx，应对：xxx）

**风险点识别**：
1. xxx
2. xxx
3. xxx

**风险损失统计**：
- 市场风险损失：XX 万
- 交易风险损失：XX 万
- 操作风险损失：XX 万

## 五、总结与改进

**做得好的**：
1. xxx
2. xxx

**需要改进的**：
1. xxx
2. xxx

**明日计划**：
1. xxx
2. xxx
```

### 模板 C：改进版
> 适用："改进计划""团队复盘"

```
**盘后复盘** | YYYY-MM-DD

**核心结论**：xxx

**关键指标**：

| 指标 | 目标 | 实际 | 差异 | 分析 |
|-----|------|------|------|------|
| 收益率 | XX% | XX% | XX% | xxx |
| 交易纪律 | XX% | XX% | XX% | xxx |
| 风险事件 | 0 | XX | XX | xxx |

**重大问题根因分析**：

**问题 1**：xxx
- 直接原因：xxx
- 间接原因：xxx
- 根本原因：xxx
- 改进措施：xxx
- 责任人：xxx
- 完成时间：xxx

**问题 2**：xxx
- 直接原因：xxx
- 间接原因：xxx
- 根本原因：xxx
- 改进措施：xxx
- 责任人：xxx
- 完成时间：xxx

**改进计划**：

| 改进项 | 措施 | 责任人 | 时间 | 验收标准 |
|-------|------|-------|------|---------|
| xxx | xxx | xxx | xxx | xxx |

**经验沉淀**：
- 可复用经验：xxx
- 需避免错误：xxx

**后续跟踪**：
- 跟踪事项：xxx
- 跟踪人：xxx
```

---

## 特殊情况处理

**数据不完整**：基于已有数据生成复盘，说明"完整复盘需 XX 数据"

**无重大风险/问题**：如实报告"今日无重大风险事件"，总结做得好的方面

**多组合/多账户**：按组合/账户分别复盘，再汇总整体情况

**重大亏损/风险事件**：单独列示，深度分析根因，形成专项改进计划

---

## 语言要求

- 先给结论，再给支撑数据
- 复盘要客观，不回避问题，不夸大成绩
- 明确区分：事实描述 vs 原因分析 vs 改进措施
- 关键数字、问题点、改进项单独指出
- 改进措施要具体、可执行、可追踪

---

## Reference

**复盘方法论：**
- AAR（After Action Review）美军复盘法
- PDCA 循环（Plan-Do-Check-Act）
- 5Why 根因分析法
- 鱼骨图分析法

**投资复盘框架：**
- 投资日记模板
- 交易复盘清单
- 组合归因分析框架

**行业实践：**
- 券商自营盘后复盘流程
- 私募基金交易日志模板
- 量化策略复盘框架

---

## Scripts

**Python 复盘分析示例：**
```python
import pandas as pd
import numpy as np

def trade_analysis(trade_df):
    """交易分析"""
    analysis = {
        'total_trades': len(trade_df),
        'winning_trades': (trade_df['pnl'] > 0).sum(),
        'losing_trades': (trade_df['pnl'] < 0).sum(),
        'win_rate': (trade_df['pnl'] > 0).sum() / len(trade_df) * 100,
        'avg_win': trade_df[trade_df['pnl'] > 0]['pnl'].mean(),
        'avg_loss': trade_df[trade_df['pnl'] < 0]['pnl'].mean(),
        'profit_factor': trade_df[trade_df['pnl'] > 0]['pnl'].sum() / abs(trade_df[trade_df['pnl'] < 0]['pnl'].sum())
    }
    return analysis

def contribution_analysis(holdings_df, benchmark_return):
    """个股贡献分析"""
    holdings_df['contribution'] = holdings_df['weight'] * holdings_df['return']
    top_positive = holdings_df.nlargest(3, 'contribution')[['stock_name', 'contribution']]
    top_negative = holdings_df.nsmallest(3, 'contribution')[['stock_name', 'contribution']]
    
    # 归因分析
    active_return = holdings_df['contribution'].sum() - benchmark_return
    selection_effect = (holdings_df['return'] - benchmark_return).sum() / len(holdings_df)
    allocation_effect = active_return - selection_effect
    
    return {
        'top_positive': top_positive.to_dict('records'),
        'top_negative': top_negative.to_dict('records'),
        'active_return': active_return,
        'selection_effect': selection_effect,
        'allocation_effect': allocation_effect
    }

def generate_review_summary(market_data, portfolio_data, trade_data):
    """生成复盘摘要"""
    return {
        'market_summary': {
            'index_change': market_data['index_change'].iloc[-1],
            'sentiment': 'positive' if market_data['index_change'].iloc[-1] > 0 else 'negative'
        },
        'portfolio_performance': {
            'daily_return': portfolio_data['daily_return'].iloc[-1],
            'daily_pnl': portfolio_data['daily_pnl'].iloc[-1]
        },
        'trade_analysis': trade_analysis(trade_data),
        'risk_events': portfolio_data['risk_events'].tolist() if 'risk_events' in portfolio_data else []
    }
```

**SQL 查询示例：**
```sql
-- 查询当日交易复盘数据
SELECT 
    '交易统计' as category,
    COUNT(*) as trade_count,
    SUM(pnl) as total_pnl,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as win_count,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as loss_count,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as win_rate
FROM trade_table
WHERE trade_date = '2026-03-16'
UNION ALL
SELECT 
    '持仓表现',
    COUNT(DISTINCT stock_code),
    SUM(unrealized_pnl),
    SUM(CASE WHEN unrealized_pnl > 0 THEN 1 ELSE 0 END),
    SUM(CASE WHEN unrealized_pnl < 0 THEN 1 ELSE 0 END),
    NULL
FROM holdings_table
WHERE trade_date = '2026-03-16';
```
