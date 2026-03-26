---
name: a-share-alpha-decay
description: A股Alpha衰减/因子拥挤度分析。当用户说"Alpha衰减"、"alpha decay"、"因子拥挤"、"策略容量"、"因子失效"、"XX因子还有效吗"、"crowding"、"策略拥挤"时触发。分析因子/策略的Alpha随时间的衰减趋势、因子拥挤度指标、策略容量限制。支持研报风格（formal）和快速分析风格（brief）。
---

# A股Alpha衰减分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],...
```

## Workflow

### Step 1: 选择因子/策略
确定要分析 Alpha 衰减的目标：特定因子（如低 PE）或策略（如动量）

### Step 2: 分时段 IC/收益分析
1. 将历史数据分为多个子时段（如每年/每半年）
2. 分别计算各时段的 IC、因子收益率、多空组合收益
3. 观察 Alpha 随时间的变化趋势

### Step 3: 滚动窗口衰减曲线
1. 使用滚动窗口（如 252 日）计算 IC/IR
2. 绘制 IC 的时间序列，观察趋势性下降
3. 计算 IC 的结构性断点（Chow test）

### Step 4: 拥挤度指标
- **估值收敛度**：因子多头组 vs 空头组的估值差收窄
- **换手率集中度**：因子多头组的换手率异常升高
- **相关性上升**：多头组内股票相关性增加
- **策略容量**：以冲击成本估计最大可容纳资金量

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 衰减分析 | 完整时序+断点检验 | 当前 IC vs 历史均值 |
| 拥挤度 | 多维指标矩阵 | 拥挤/正常/低估 |
| 容量 | 详细估算 | 大/中/小 |

默认风格：brief。

## 关键规则
1. Alpha 衰减是正常现象——被更多人发现的因子会被套利掉
2. 区分周期性衰减（市场风格切换）和结构性衰减（因子失效）
3. A 股因子生命周期通常 3-5 年，短于美股
4. 小盘股因子容量小，衰减更快
