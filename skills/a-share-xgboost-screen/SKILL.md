---
name: a-share-xgboost-screen
description: A股XGBoost选股/梯度提升模型。当用户说"XGBoost"、"GBDT"、"梯度提升"、"LightGBM选股"、"树模型选股"、"XGB"、"机器学习选股"时触发。基于 cn-stock-data 获取数据，构建XGBoost/LightGBM选股模型。支持 formal/brief 两种输出风格。
---

# XGBoost选股/梯度提升模型助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线+技术指标
- **财务数据**: 季度财务指标
- **因子数据**: 预计算因子库

## 分析工作流

### Step 1: 特征准备
- 量价特征：收益率/波动率/换手率/动量等
- 基本面特征：PE/PB/ROE/营收增速/现金流等
- 技术特征：MACD/RSI/布林带/均线偏离等
- 特征预处理：缺失值填充/极值处理/标准化

### Step 2: 模型训练
- LightGBM vs XGBoost：LightGBM更快，效果相当
- 标签定义：下期N日超额收益(行业中性化后)
- Purged K-Fold交叉验证：防止前视偏差
- 超参数：max_depth=6, num_leaves=63, lr=0.05

### Step 3: 特征重要性分析
- Gain重要性：特征对损失函数的贡献
- SHAP值：每个特征对每个预测的边际贡献
- 特征交互：哪些特征组合产生非线性效应
- 特征筛选：去除低重要性特征简化模型

### Step 4: 选股信号生成
- 模型预测→截面排序→选股信号
- Top N选股：选预测收益最高的N只
- 行业中性：每个行业内选Top K
- 信号衰减监控：滚动IC是否下降

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# XGBoost选股报告

## 一、模型概览
| 参数 | 设置 |
|------|------|

## 二、特征重要性
[Top10特征及SHAP值]

## 三、选股表现
[IC/多空收益/分组单调性]

## 四、本期选股
[Top股票列表与预测分数]
```

### brief 风格（快速分析）
```
## XGBoost选股速览
- LightGBM，85个特征
- IC=0.042, ICIR=1.6
- Top特征：20日动量、ROE变化、换手率
- 本期Top10：[股票列表]
```

参考 `references/xgboost-screen-guide.md` 获取详细方法论与 A股实证研究。

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
