---
name: a-share-sentiment
description: A股市场情绪综合研判/恐贪指数/情绪面分析。当用户说"市场情绪"、"情绪面"、"恐慌"、"贪婪"、"sentiment"、"现在市场情绪怎么样"、"市场热度"、"赚钱效应"、"亏钱效应"、"市场温度"、"是不是过热了"、"恐贪指数"、"情绪综合研判"时触发。MUST USE when user asks about market sentiment, fear/greed index, market temperature, or whether the market is overheated/panicking. 聚合多维数据（涨跌比/换手率/涨停数/北向资金/融资余额/成交量等），构建市场情绪综合判断。支持研报风格（formal）和快速解读风格（brief）。
---

# A股市场情绪分析助手

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 大盘行情（涨跌数据、成交量）
python "$SCRIPTS/cn_stock_data.py" quote --code SH000001,SZ399001,SZ399006

# 北向资金
python "$SCRIPTS/cn_stock_data.py" north_flow

# 大盘K线（近期趋势，用于历史对比）
python "$SCRIPTS/cn_stock_data.py" kline --code SH000001 --freq daily --start $(date -v-30d +%Y-%m-%d)

# 资金流向（全市场）
python "$SCRIPTS/cn_stock_data.py" fund_flow --code SH000001
```

补充数据（通过 akshare 或 web 搜索获取）：
- 融资余额变化
- 两市成交额
- 涨停/跌停家数
- 新股上市表现

## Workflow

### Step 1: 数据采集
从多个维度获取市场情绪数据，优先使用 cn-stock-data 脚本，不足部分用 akshare 或 web 搜索补充。

### Step 2: 指标计算
- 涨跌比：上涨家数 / 下跌家数
- 涨停/跌停数量
- 两市成交额（与近20日均值对比）
- 换手率水平
- 北向资金净流向（当日 + 5日累计）
- 融资余额变化方向

### Step 3: 情绪评分
将各维度归一化为 0-100 分，加权平均得到综合评分：
- **0-20**: 极度恐慌
- **20-40**: 偏悲观
- **40-60**: 中性
- **60-80**: 偏乐观
- **80-100**: 极度贪婪

详细评分体系见 `references/sentiment-indicators.md`。

### Step 4: 历史对比
当前情绪在近1年中的百分位位置，参考历史极端值校准。

### Step 5: 输出

## 输出风格

| 维度 | formal（研报风格） | brief（快速解读） |
|------|-------------------|------------------|
| 输出 | 完整市场情绪报告 | 情绪温度计 + 核心结论 |
| 指标 | 8-10个维度逐一分析 | 综合评分 + 3个关键指标 |
| 历史对比 | 与近1年百分位对比 | 简单高/低判断 |
| 结论 | 客观描述（"情绪处于偏乐观区间"） | 可加判断 |

默认使用 formal 风格；用户要求"简单说说"、"快速看下"时用 brief。

## 关键规则

1. **情绪指标是辅助工具**，不能单独作为交易依据
2. **极端情绪往往是反向指标**：极度恐慌可能是底部，极度贪婪可能是顶部
3. **不同市场阶段权重不同**：牛市重点看成交量，熊市重点看跌停数
4. **标注数据时效性**：明确说明是当日盘中数据还是上一交易日收盘数据
5. **结构性行情需特别说明**：部分板块热+部分板块冷时，全市场情绪指标可能失真
6. **政策敏感性**：重磅政策可一日扭转情绪，需关注最新政策信息
