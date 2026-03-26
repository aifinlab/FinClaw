---
name: a-share-event-quant
description: A股事件驱动量化/事件研究法。当用户说"事件研究"、"event study"、"事件驱动量化"、"公告效应"、"CAR"、"异常收益"、"XX公告后会怎样"、"事件窗口"时触发。基于 cn-stock-data 获取K线数据，运用事件研究法量化分析特定事件对股价的影响。支持研报风格（formal）和快速分析风格（brief）。
---

# A股事件驱动量化

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" kline --code SH000300 --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
```
补充：通过 web 搜索获取事件日期、公告内容。

## Workflow

### Step 1: 定义事件与事件日
- 明确事件类型（业绩预告/定增/回购/高管增持等）
- 确定精确的事件日（公告日 T=0）

### Step 2: 设定窗口
- 估计窗口：[-250, -11]（用于估计正常收益模型）
- 事件窗口：[-10, +10] 或 [-5, +20]（观察异常收益）

### Step 3: 计算正常收益（市场模型）
- R_normal = α + β × R_market
- α, β 在估计窗口内通过 OLS 回归得到

### Step 4: 计算异常收益
- AR_t = R_actual - R_normal（每日异常收益）
- CAR = Σ AR_t（累计异常收益）
- CAAR = mean(CAR) across events（平均累计异常收益）

### Step 5: 统计检验 + 输出
- t 检验：CAR / (σ_AR × √T)
- |t| > 1.96 → 5% 水平显著

| 维度 | formal | brief |
|------|--------|-------|
| 模型 | 市场模型+Fama-French | 市场模型 |
| 检验 | 多种统计量 | 仅 t 统计量 |
| 图表 | CAR 时序图+置信区间 | CAR 数值 |

默认风格：brief。

## 关键规则
1. 事件日必须精确——公告日 vs 实施日区别很大
2. A 股盘后公告次日生效，需注意 T+1 定义
3. 避免事件窗口重叠（同一股票短期内多个事件）
4. 样本量 > 30 才有统计意义

## 使用示例

### 示例 1: 基本使用

```python
# 调用 skill
result = run_skill({
    "param1": "value1",
    "param2": "value2"
})
```

### 示例 2: 命令行使用

```bash
python scripts/run_skill.py --input data.json
```
