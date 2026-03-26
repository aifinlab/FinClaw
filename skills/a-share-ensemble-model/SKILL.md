---
name: a-share-ensemble-model
description: A股集成模型/多模型融合策略。当用户说"集成模型"、"ensemble"、"模型融合"、"stacking"、"blending"、"多模型"、"模型组合"时触发。基于 cn-stock-data 获取数据，构建多模型集成策略。支持 formal/brief 两种输出风格。
---

# 集成模型/多模型融合助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线历史数据
- **因子数据**: 预计算因子库
- **模型预测**: 各子模型的预测结果

## 分析工作流

### Step 1: 子模型构建
- 模型多样性：LightGBM/XGBoost/线性/MLP/LSTM
- 特征多样性：不同特征子集训练不同模型
- 时间多样性：不同训练窗口/更新频率
- 标签多样性：不同预测周期(5日/10日/20日)

### Step 2: 集成方法选择
- 简单平均：等权平均各模型预测
- 加权平均：按历史IC加权
- Stacking：用元模型学习最优组合权重
- Blending：holdout集上训练组合权重

### Step 3: 集成效果评估
- 集成IC vs 单模型IC：集成应显著提升
- 集成稳定性：IC波动率应降低
- 模型贡献度：各子模型对集成的边际贡献
- 冗余检测：去除贡献为负的子模型

### Step 4: 动态集成
- 时变权重：根据近期表现动态调整权重
- 市场状态适配：不同市场状态用不同权重
- 在线学习：实时更新集成权重
- 模型淘汰：持续表现差的模型自动降权

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# 集成模型报告

## 一、子模型概览
| 模型 | IC | 权重 |
|------|-----|------|

## 二、集成表现
[集成IC/Sharpe vs 单模型]

## 三、模型贡献
[各模型边际贡献分析]

## 四、当期信号
[集成预测Top/Bottom]
```

### brief 风格（快速分析）
```
## 集成模型速览
- 5个子模型加权集成
- 集成IC=0.055 vs 最优单模型0.042
- Sharpe提升 +0.4
- 本期集成Top10：[股票列表]
```

参考 `references/ensemble-model-guide.md` 获取详细方法论与 A股实证研究。

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
