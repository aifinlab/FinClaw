---
name: a-share-automl-strategy
description: A股AutoML策略/自动化量化建模。当用户说"AutoML"、"自动建模"、"自动机器学习"、"auto ML"、"自动化策略"、"一键建模"时触发。基于 cn-stock-data 获取数据，使用AutoML自动构建量化策略。支持 formal/brief 两种输出风格。
---

# AutoML策略/自动化建模助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线历史数据
- **因子数据**: 预计算因子库
- **财务数据**: 季度财务指标

## 分析工作流

### Step 1: 自动特征工程
- 自动生成：滞后/滚动/差分/交叉特征
- 特征选择：基于互信息/方差/相关性自动筛选
- 特征变换：Box-Cox/分位数变换/PCA降维
- 目标编码：类别特征的自动编码

### Step 2: 模型自动搜索
- 候选模型池：LightGBM/XGBoost/CatBoost/线性模型/MLP
- 超参数搜索：Bayesian Optimization/TPE
- 模型集成：自动Stacking/Blending
- 搜索预算：限制总训练时间/模型数量

### Step 3: 自动验证
- 时序交叉验证：自动设置Purged K-Fold
- 多指标评估：IC/Sharpe/最大回撤同时优化
- 过拟合检测：训练集vs验证集性能差距
- 稳定性检验：不同时间窗口的表现一致性

### Step 4: 策略输出
- 最优模型及其配置
- 特征重要性排序
- 预测信号与选股列表
- 模型更新建议：何时需要重训练

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# AutoML量化策略报告

## 一、搜索结果
| 模型 | IC | Sharpe | 排名 |
|------|-----|--------|------|

## 二、最优模型
[模型配置、特征重要性]

## 三、策略表现
[回测结果、风险指标]

## 四、部署建议
[更新频率、监控指标]
```

### brief 风格（快速分析）
```
## AutoML速览
- 搜索50个模型，最优：LightGBM
- IC=0.045, Sharpe 2.0
- Top特征：动量+质量+资金流
- 建议：月度重训练，监控IC衰减
```

参考 `references/automl-strategy-guide.md` 获取详细方法论与 A股实证研究。
