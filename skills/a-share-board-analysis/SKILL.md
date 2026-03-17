---
name: a-share-board-analysis
description: A股涨跌停板分析/连板追踪/涨停板统计。当用户说"涨停"、"跌停"、"涨停板"、"连板"、"打板"、"炸板"、"涨停分析"、"今天多少家涨停"、"连板股"、"首板"、"二板"、"三板"、"涨停原因"、"XX涨停了"、"涨停板分析"时触发。MUST USE when user asks about limit-up/limit-down board analysis, consecutive board tracking, or daily limit statistics for A-shares. 分析当日涨跌停数量、连板梯队、涨停原因归类、炸板率，追踪连板龙头股走势。支持研报风格（formal）和快速解读风格（brief）。
---

# A股涨跌停板分析助手

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 涨停池（当日涨停股票列表，含连板天数、涨停原因等）
python -c "import akshare as ak; df=ak.stock_zt_pool_em(date='YYYYMMDD'); print(df.to_json(orient='records', force_ascii=False))"

# 跌停池（当日跌停股票列表）
python -c "import akshare as ak; df=ak.stock_zt_pool_dtgc_em(date='YYYYMMDD'); print(df.to_json(orient='records', force_ascii=False))"

# 炸板池（当日曾触及涨停但未封住的股票）
python -c "import akshare as ak; df=ak.stock_zt_pool_zbgc_em(date='YYYYMMDD'); print(df.to_json(orient='records', force_ascii=False))"

# 强势股池（当日涨幅较大的非涨停股）
python -c "import akshare as ak; df=ak.stock_zt_pool_strong_em(date='YYYYMMDD'); print(df.to_json(orient='records', force_ascii=False))"

# 个股行情（通过 cn-stock-data）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]

# K线（看连板股历史走势）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
```

补充：通过 web 搜索确认涨停原因/题材概念。

## Workflow

### Step 1: 确定分析范围

根据用户意图分类：
- **当日涨跌停全景**：今日涨停/跌停家数、连板梯队、炸板率
- **特定连板梯队**：几板股有哪些、最高连板股是谁
- **个股涨停原因**：某只股票为何涨停/跌停

### Step 2: 数据获取

获取涨停池 + 跌停池 + 炸板池数据。如分析个股，额外获取该股 K 线和行情报价。日期参数用 YYYYMMDD 格式，默认为最近交易日。

> 注意：非交易日或盘中时段数据可能不完整，需注明数据状态。

### Step 3: 涨跌停分析

- **涨跌停对比**：涨停家数 vs 跌停家数，判断市场情绪（涨多跌少=偏强）
- **连板梯队**：按连板天数分层统计（首板/二板/三板/四板及以上）
- **板块归类**：涨停股按所属概念/行业分组，找出最强主线
- **炸板率**：炸板数 /（涨停数 + 炸板数），炸板率高=封板意愿弱、市场分歧大
- **涨停时间**：早盘集合竞价/开盘涨停 vs 尾盘涨停，时间越早封板越强

> 详见 [references/board-analysis-guide.md](references/board-analysis-guide.md) 中的涨跌停制度和连板术语。

### Step 4: 连板龙头追踪

- 识别当日最高连板股（"最高标"）
- 获取该股近期 K 线，分析连板启动原因和走势
- 对比同期次高标和跟风股
- 连板断板后的走势预警（高位断板常伴随大幅回调）

### Step 5: 输出

根据风格生成报告：

| 维度 | formal | brief |
|------|--------|-------|
| 输出格式 | 完整涨跌停复盘报告 | 快速要点 |
| 连板梯队 | 逐层详列+个股点评 | 仅列最高板和关键股 |
| 板块归类 | 分行业/概念详细归类 | 仅标注最强主线 |
| 炸板分析 | 炸板股逐只分析 | 仅炸板率数字 |
| 结论 | 客观陈述市场情绪 | 可加简要判断 |

默认风格：brief。用户要求"详细分析"/"出报告"/"复盘"时用 formal。

## 关键规则

1. **涨跌停制度因板块而异**：主板10%、科创板/创业板20%、北交所30%、ST股5%，分析时必须区分
2. **连板≠安全**：高连板股随时可能断板，绝不暗示"还能继续涨停"
3. **注明数据日期**：始终标注分析的是哪一天的数据，避免误导
4. **不做涨停预测**：不说"明天会涨停"、"可以打板"等预测性建议
5. **炸板风险**：炸板股风险极大（冲高回落），需特别提示
6. **数据时效**：涨停池数据盘中实时更新，收盘后为最终数据，需说明取数时点
