---
name: a-share-stock-review
description: A股个股复盘/交易复盘/个股走势回顾分析。当用户说"个股复盘"、"复盘"、"今天XX怎么回事"、"XX为什么涨"、"XX为什么跌"、"XX走势分析"、"stock review"、"盘后分析"、"XX今天异动"、"复盘分析"、"个股复盘分析"、"XX今天走势"、"XX涨跌原因"时触发。MUST USE when user asks about stock review, post-market analysis, why a stock went up/down today, or wants to review a specific stock's recent performance. 针对单只股票的当日或近期走势进行全面复盘，包括股价表现、量能变化、资金流向、消息面驱动因素。支持详细复盘风格（formal）和快速解读风格（brief）。
---

# A股个股复盘 Skill

## 数据获取

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 实时行情（价格/涨跌幅/换手率/量比/振幅等）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]

# 近20日K线（趋势/支撑压力/均线）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [20日前YYYYMMDD]

# 资金流向（主力/散户净流入）
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE]

# 基本财务数据（市盈率/市净率/总市值等）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

补充数据源：用 web 搜索获取当日公告、新闻、研报等消息面信息。

## Workflow

### Step 1: 数据采集
- 并行获取 quote / kline / fund_flow / finance 四组数据
- Web 搜索"[股票名称] 今日 公告 新闻"获取消息面

### Step 2: 股价表现分析
- 当日涨跌幅、振幅、最高/最低价、收盘价位置（靠近高点or低点）
- 换手率高低判断（与近20日均值对比）
- 量比分析（>2放量、<0.5缩量）
- 与大盘/行业指数对比（相对强弱）

### Step 3: 资金流向分析
- 主力净流入/流出金额及占比
- 超大单/大单/中单/小单资金分布
- 近5日资金流向趋势（持续流入or流出）

### Step 4: 消息面梳理
- 公司公告（业绩预告/重大事项/股东变动等）
- 行业新闻/政策（利好or利空）
- 研报观点（目标价/评级变动）
- 市场热点关联（概念板块/题材）

### Step 5: 综合复盘结论
- 一句话核心结论：涨跌原因归因
- 后续关注要点（支撑位/压力位/事件催化）
- 风险提示

## 输出风格

- **formal**: 按模板7节完整输出，适合盘后深度复盘，参见 `references/stock-review-template.md`
- **brief**: 一段话快速解读（3-5句），适合快速了解
- 默认使用 formal 风格；用户要求"简单说说"、"快速看看"时用 brief

## 注意事项

- 股票代码自动补全：用户说"贵州茅台"时自动识别为 600519
- 日期默认当日（交易日），非交易日回退到最近交易日
- 涨停/跌停/异动情况需特别标注并重点分析原因
- 数据不可用时明确告知，不编造数据
- 所有结论必须基于数据，标注数据来源
