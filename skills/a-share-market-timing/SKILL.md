---
name: a-share-market-timing
description: A股择时策略/大盘择时信号。当用户说"择时"、"market timing"、"该不该进场"、"现在能买吗"、"仓位建议"、"大盘择时"时触发。量化分析大盘择时信号。支持formal和brief风格。
---
# A股择时策略/大盘择时信号
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取大盘指数数据
### Step 2: 多维择时信号
- 技术面：均线系统/MACD/布林带
- 资金面：北向资金/融资余额/成交量
- 情绪面：涨跌家数/涨停数/新高数
- 估值面：PE分位/PB分位/股债利差
### Step 3: 综合评分
各维度加权打分(0-100)
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 各维度评分 | 详细指标明细 | 综合分数 |
| 仓位建议 | 分档仓位表 | 建议仓位 |
| 历史对照 | 类似评分历史表现 | 无 |
默认风格：brief。
## 关键规则
1. 择时极难——大多数择时策略长期跑不赢满仓持有
2. 左侧择时（抄底/逃顶）风险极高
3. 右侧择时（趋势确认后行动）更稳健
4. 多信号综合比单一信号更可靠
5. 择时错误的代价是踏空——宁可少赚不可大亏
