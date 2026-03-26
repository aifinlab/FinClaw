---
name: a-share-ml-stock-predict
description: A股ML股价预测/收益率预测。当用户说"ML预测"、"机器学习预测"、"股价预测"、"收益率预测"、"预测模型"、"ML选股"时触发。基于 cn-stock-data 获取数据，构建ML预测模型。支持 formal/brief 两种输出风格。
---

# ML股价预测/收益率预测助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线+技术指标
- **财务数据**: 季度财务指标
- **另类数据**: 舆情/资金流等

## 分析工作流

### Step 1: 特征工程
- 技术特征：均线/MACD/RSI/布林带等50+指标
- 基本面特征：PE/PB/ROE/营收增速等
- 资金流特征：主力净流入/北向资金/融资余额
- 时序特征：滞后收益率、波动率、换手率

### Step 2: 模型训练
- LightGBM/XGBoost：表格数据首选
- 训练标签：下期N日收益率(回归)或涨跌方向(分类)
- 时序交叉验证：Purged K-Fold避免前视偏差
- 超参数优化：Optuna/Bayesian Optimization

### Step 3: 模型评估
- 回归：IC/ICIR/MSE/MAE
- 分类：AUC/Precision/Recall/F1
- 经济指标：多空收益/Sharpe/最大回撤
- 样本外滚动测试：每月重训练

### Step 4: 模型部署与监控
- 预测信号生成：每日收盘后运行模型
- 信号衰减监控：IC滚动均值是否下降
- 模型漂移检测：特征分布变化预警
- 定期重训练：月度/季度更新模型

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# ML收益率预测报告

## 一、模型概览
| 模型 | 特征数 | 训练期 |
|------|--------|--------|

## 二、预测表现
[IC/ICIR/多空收益]

## 三、当期预测
[Top/Bottom股票列表]

## 四、模型健康度
[漂移检测、信号衰减]
```

### brief 风格（快速分析）
```
## ML预测速览
- LightGBM模型，128个特征
- 样本外IC=0.04, ICIR=1.5
- 本期Top10预测：[股票列表]
- 模型健康：信号稳定，无漂移
```

参考 `references/ml-stock-predict-guide.md` 获取详细方法论与 A股实证研究。

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
