---
name: a-share-lstm-forecast
description: A股LSTM时序预测/序列建模。当用户说"LSTM"、"时序预测"、"序列模型"、"RNN预测"、"GRU"、"循环神经网络"、"LSTM预测股价"时触发。基于 cn-stock-data 获取数据，构建LSTM时序预测模型。支持 formal/brief 两种输出风格。
---

# LSTM时序预测/序列建模助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线序列(至少3年)
- **技术指标**: 预计算的技术特征
- **宏观数据**: 利率/汇率等外部序列

## 分析工作流

### Step 1: 序列数据准备
- 滑动窗口：过去N天数据预测未来M天
- 特征标准化：Z-score或MinMax归一化
- 序列长度选择：通常20-60个交易日
- 多变量输入：OHLCV+技术指标+外部变量

### Step 2: LSTM模型构建
- 网络结构：1-3层LSTM + Dense输出层
- 隐藏单元数：64-256，视数据量调整
- Dropout：0.2-0.5防止过拟合
- 变体选择：LSTM/GRU/Bi-LSTM/Attention-LSTM

### Step 3: 训练策略
- 损失函数：MSE(回归)/CrossEntropy(分类)
- 优化器：Adam，学习率1e-3→1e-4衰减
- Early Stopping：验证集loss不降则停止
- 时序分割：严格按时间划分训练/验证/测试

### Step 4: 预测与应用
- 点预测：未来1-5日收益率/价格
- 区间预测：预测值±置信区间
- 方向预测：涨跌概率输出
- 集成预测：多个LSTM模型投票/平均

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# LSTM时序预测报告

## 一、模型配置
| 参数 | 设置 |
|------|------|

## 二、预测表现
[MSE/方向准确率/IC]

## 三、当期预测
[未来N日预测值与置信区间]

## 四、模型诊断
[残差分析、过拟合检查]
```

### brief 风格（快速分析）
```
## LSTM预测速览
- 2层LSTM，隐藏128，窗口30天
- 方向准确率 56%，IC=0.03
- 预测明日：涨概率 62%
- 5日预测区间：[24.8, 26.2]
```

参考 `references/lstm-forecast-guide.md` 获取详细方法论与 A股实证研究。

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
