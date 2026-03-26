---
name: a-share-price-impact-model
description: A股价格冲击模型/Kyle Lambda分析。当用户说"价格冲击模型"、"Kyle Lambda"、"lambda"、"冲击系数"、"价格影响模型"、"订单流冲击"时触发。基于 cn-stock-data 获取数据，估计价格冲击模型参数。支持 formal/brief 两种输出风格。
---

# 价格冲击模型/Kyle Lambda分析助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **逐笔成交**: 成交价格/量/方向
- **盘口数据**: 市场深度
- **日线数据**: 日均成交量/波动率

## 分析工作流

### Step 1: Kyle Lambda估计
- 回归模型：ΔP = λ × OFI + ε
- OFI = 签名订单流(买入为正，卖出为负)
- λ = 价格冲击系数，单位：元/手或bps/百万元
- 不同时间尺度的Lambda：tick级/分钟级/日级

### Step 2: 非线性冲击模型
- 平方根模型：Impact = σ × √(Q/ADV)
- 幂律模型：Impact = α × (Q/ADV)^β，β通常0.4-0.6
- 临时冲击 vs 永久冲击的分离
- Almgren模型：线性临时+线性永久

### Step 3: 冲击因素分析
- 市值效应：小盘股Lambda是大盘股的3-5倍
- 波动率效应：高波动时Lambda增大
- 流动性效应：成交量大时Lambda减小
- 信息效应：知情交易的冲击大于噪声交易

### Step 4: 冲击模型应用
- 最优执行：基于冲击模型的最优拆单
- 交易成本预测：给定订单量预测冲击成本
- 流动性评分：Lambda作为流动性的综合度量
- 市场质量评估：Lambda越小市场质量越高

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# [标的] 价格冲击模型报告

## 一、Lambda估计
| 时间尺度 | Lambda | R² |
|---------|--------|-----|

## 二、非线性模型
[平方根/幂律模型参数]

## 三、冲击因素
[市值/波动率/流动性影响]

## 四、应用建议
```

### brief 风格（快速分析）
```
## [标的] 冲击模型速览
- Kyle Lambda = 0.15 bps/百万元
- 平方根模型β = 0.52
- 10万股订单预期冲击 0.08%
- 流动性评分：良好(Lambda P35)
```

参考 `references/price-impact-model-guide.md` 获取详细方法论与 A股实证研究。

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
