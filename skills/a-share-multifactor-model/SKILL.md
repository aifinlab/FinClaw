---
name: a-share-multifactor-model
description: A股多因子模型/Barra风格因子分析。当用户说"多因子"、"multifactor"、"Barra"、"因子模型"、"风格因子"、"XX的因子暴露"、"因子收益率"、"风险模型"时触发。基于 cn-stock-data 获取行情和财务数据，构建多因子风险模型，分析因子暴露、因子收益、协方差矩阵。支持研报风格（formal）和快速分析风格（brief）。
---

# A股多因子模型

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 个股K线（计算动量/波动率因子）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]

# 实时行情（市值/PE/PB等）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],...

# 财务指标（ROE/营收增速等基本面因子）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

**量化计算**：
```bash
QSCRIPTS="$SKILLS_ROOT/a-share-multifactor-model/scripts"
# 多因子回归
python "$QSCRIPTS/multifactor_builder.py" --returns returns.csv --factors "size,value,momentum" --method ols
```

## Workflow

### Step 1: 确定因子体系
根据用户需求选择因子集：
- **Barra CNE5 风格**：Size/Beta/Momentum/ResidVol/NLSize/BP/Liquidity/EarningsYield/Growth/Leverage
- **自定义因子**：用户指定的因子组合
- 通过 cn-stock-data 获取原始数据（行情+财务）

### Step 2: 因子计算与标准化
1. 从原始数据计算因子值
2. 去极值（MAD 法 ±3 倍）
3. 标准化（Z-score）
4. 缺失值处理（行业均值填充）

### Step 3: 截面回归估计因子收益
1. 每期对股票收益 vs 因子暴露做 OLS 回归
2. 回归系数即为因子收益率
3. 计算因子收益的 t 统计量

### Step 4: 构建风险模型
1. 因子协方差矩阵（指数加权）
2. 特质风险估计（回归残差的波动率）
3. 股票层面的风险分解

### Step 5: 输出

| 维度 | formal（完整因子报告） | brief（快速分析） |
|------|---------------------|-------------------|
| 因子定义 | 完整因子体系说明 | 仅列出因子名 |
| 因子收益 | 完整时序+统计检验 | 近期因子收益排名 |
| 暴露分析 | 个股因子暴露详表 | 关键因子暴露值 |
| 风险模型 | 协方差矩阵+特质风险 | 无 |
| 图表 | 因子收益累计曲线 | 无 |

默认风格：brief。用户要求"详细"/"完整模型"时切换为 formal。

## 关键规则
1. 因子暴露需经行业和市值中性化处理
2. 因子协方差使用半衰期 90 天的指数加权
3. 特质收益率需检验正态性假设
4. A 股需剔除 ST 股和次新股（上市<60日）
5. 行业分类默认使用申万一级（31 个行业）
