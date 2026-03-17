---
name: a-share-order-imbalance
description: A股委托不平衡/买卖盘口分析。当用户说"委托不平衡"、"order imbalance"、"买卖盘"、"盘口"、"挂单"、"买盘强还是卖盘强"时触发。量化分析盘口委托数据。支持formal和brief风格。
---
# A股委托不平衡/买卖盘口分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取实时行情（含买卖五档）
### Step 2: 计算委托不平衡
OIB = (买委托量 - 卖委托量) / (买委托量 + 卖委托量)
### Step 3: 内外盘分析
- 内盘（主动卖）vs 外盘（主动买）比例
- 大单占比分析
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| OIB | 时序分析+统计 | 当前OIB |
| 盘口 | 五档详细分析 | 买/卖主导 |
默认风格：brief。
## 关键规则
1. A股盘口可能被操纵——大单挂撤频繁
2. OIB对短期价格有预测力但衰减快
3. 集合竞价盘口比连续竞价更有参考价值
4. 涨跌停板附近的盘口失真——不可直接使用
5. 高频盘口数据需注意延迟问题
