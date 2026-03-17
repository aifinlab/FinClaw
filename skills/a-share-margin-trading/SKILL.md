---
name: a-share-margin-trading
description: A股融资融券/两融分析。当用户说"融资融券"、"两融"、"融资余额"、"融券"、"margin trading"、"杠杆资金"、"融资盘"、"XX的融资余额"、"两融风向"、"杠杆水平"时触发。基于 akshare 融资融券数据和 cn-stock-data 行情数据，分析全市场两融趋势、个股融资融券变化、杠杆资金方向判断。支持研报风格（formal）和快速解读风格（brief）。不适用于北向资金（用 a-share-northbound）或基金持仓（用 a-share-fund-holding）。
---

# A股融资融券分析助手

## 数据源

```bash
# 融资融券数据（通过 akshare）
# 全市场融资融券汇总
python -c "import akshare as ak; df=ak.stock_margin_sse(start_date='20260101'); print(df.to_json(orient='records', force_ascii=False))"

# 个股融资融券明细
python -c "import akshare as ak; df=ak.stock_margin_detail_sse(date='20260315'); print(df.to_json(orient='records', force_ascii=False))"

# 行情数据
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
```

> akshare 接口名可能随版本变化，如接口不可用，通过 web 搜索获取融资融券数据。

## Workflow

### Step 1: 确定分析模式

- **全市场两融趋势分析**：大盘融资余额走势、杠杆水平变化
- **个股融资融券分析**：单只股票的两融数据变动
- **行业板块两融对比**：多只标的横向比较

### Step 2: 数据获取

获取融资余额/融券余额时间序列 + 个股行情数据。

### Step 3: 趋势分析

- 融资余额变化趋势（环比/同比）
- 融资买入额 vs 融资偿还额（净买入方向）
- 融券卖出量变化（做空力量）
- 两融余额占流通市值比（杠杆水平）

### Step 4: 信号研判

- 融资余额与大盘走势的相关性
- 融资余额创新高/新低的信号含义
- 个股融资余额异常变动（突增/骤降）
- 融券余额上升 = 做空力量增强

### Step 5: 输出

## 风格

| 维度 | formal | brief |
|------|--------|-------|
| 输出 | 完整两融分析报告 | 快速要点 |
| 时间跨度 | 3-6个月趋势 | 近1-2周变化 |
| 分析深度 | 市场+行业+个股三层 | 仅关注核心方向 |
| 图表 | 融资余额走势图数据 | 无 |

## 关键规则

1. 融资余额上升不等于看多（可能是杠杆加仓后的风险累积）
2. 融资融券数据为 T+1 披露
3. 两融标的有限制（不是所有股票都可融资融券）
4. 需结合大盘环境解读（牛市加杠杆 vs 熊市去杠杆）

## 参考

详见 [references/margin-trading-guide.md](references/margin-trading-guide.md)
