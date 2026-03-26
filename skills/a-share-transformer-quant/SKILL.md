---
name: a-share-transformer-quant
description: A股Transformer量化/注意力机制因子。当用户说"Transformer"、"注意力机制"、"attention"、"自注意力"、"Transformer量化"、"GPT选股"时触发。基于 cn-stock-data 获取数据，构建Transformer量化模型。支持 formal/brief 两种输出风格。
---

# Transformer量化/注意力因子助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线序列+截面数据
- **因子数据**: 多因子截面矩阵
- **关系数据**: 行业/供应链关系

## 分析工作流

### Step 1: 输入编码
- 时序编码：位置编码+时间特征嵌入
- 截面编码：股票特征向量化
- 多头注意力：不同head关注不同模式
- 跨股票注意力：捕获股票间的关联关系

### Step 2: 模型架构
- Temporal Transformer：时序维度自注意力
- Cross-sectional Transformer：截面维度注意力
- Spatial-Temporal Transformer：时空联合建模
- 轻量化：Performer/Linformer降低计算复杂度

### Step 3: 注意力因子提取
- 注意力权重可视化：模型关注哪些时间步/股票
- 注意力得分作为因子：高注意力=高信息量
- 动态因子权重：Transformer自动学习因子组合权重
- 跨股票注意力→行业/概念关联度因子

### Step 4: 训练与评估
- 预训练+微调：先在大量股票数据上预训练
- 排序损失：ListMLE/ApproxNDCG优化排序
- 计算资源：GPU训练，推理可CPU
- 与传统模型对比：Transformer vs LightGBM

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# Transformer量化报告

## 一、模型架构
| 组件 | 配置 |
|------|------|

## 二、注意力分析
[注意力权重可视化、关键时间步]

## 三、信号表现
[IC/多空收益/与传统模型对比]

## 四、当期信号
[Top/Bottom股票列表]
```

### brief 风格（快速分析）
```
## Transformer量化速览
- 6层Transformer，8头注意力
- IC=0.055，优于LightGBM(0.04)
- 注意力集中在近5日量价变化
- 本期Top信号：[股票列表]
```

参考 `references/transformer-quant-guide.md` 获取详细方法论与 A股实证研究。

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
