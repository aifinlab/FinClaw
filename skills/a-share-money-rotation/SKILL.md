---
name: a-share-money-rotation
description: A股资金轮动/板块资金流量化分析。当用户说"资金轮动"、"money rotation"、"板块资金流"、"资金去哪了"、"哪个板块在吸金"、"资金迁移"、"轮动节奏"时触发。基于 cn-stock-data 获取多板块资金流向数据，量化分析资金在不同板块间的轮动规律。支持研报风格（formal）和快速分析风格（brief）。
---

# A股资金轮动分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
# 各板块代表股的资金流向
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE] --days 30
# 板块指数K线
python "$SCRIPTS/cn_stock_data.py" kline --code [INDEX_CODE] --freq daily --start [日期]
# 实时行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],...
```

**量化计算**：
```bash
QSCRIPTS="$SKILLS_ROOT/a-share-money-rotation/scripts"
python "$QSCRIPTS/rotation_tracker.py" --data sectors_flow.json --window 20
```

## Workflow

### Step 1: 获取各板块资金流向
- 选取代表性板块（消费/科技/金融/周期/医药/新能源等）
- 获取各板块主力资金净流入数据

### Step 2: 构建资金流入强度指标
- 净流入金额标准化（按板块市值归一化）
- 计算资金流入动量（近5日 vs 近20日变化率）
- 排名变化追踪

### Step 3: 识别轮动方向
- 资金从哪些板块流出 → 流入哪些板块
- 大盘/小盘轮动信号
- 价值/成长风格轮动信号

### Step 4: 轮动节奏分析
- 领先/滞后关系（板块A资金流入领先板块B几天？）
- 轮动周期（典型持续时间）
- 与大盘涨跌的关系

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 板块排名 | 全板块资金流向表 | Top 3 流入/流出 |
| 轮动方向 | 详细流向矩阵 | 一句话总结 |
| 历史对比 | 与过去轮动周期对比 | 无 |

默认风格：brief。

## 关键规则
1. 资金流向数据有噪音——需用多日平均而非单日数据
2. 主力资金≠所有资金，小单散户资金方向常常相反
3. 资金轮动往往滞后于行情——先涨后有资金流入
4. A 股典型轮动周期：2-4 周为一轮

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
