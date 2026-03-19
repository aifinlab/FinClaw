---
name: a-share-deep-learning-alpha
description: A股深度学习Alpha信号/神经网络量化。当用户说"深度学习"、"deep learning"、"神经网络量化"、"DL alpha"、"CNN选股"、"深度因子"时触发。基于 cn-stock-data 获取数据，构建深度学习Alpha模型。支持 formal/brief 两种输出风格。
---

# 深度学习Alpha信号助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **K线数据**: 日线序列(至少5年)
- **分钟数据**: 日内模式特征
- **财务+另类数据**: 多模态输入

## 分析工作流

### Step 1: 数据表示与输入构造
- 时序输入：过去D天的OHLCV+技术指标矩阵
- 截面输入：当期所有股票的因子截面
- 图像输入：K线图/分时图转为图像(CNN)
- 多模态融合：数值+文本+图像联合输入

### Step 2: 模型架构选择
- MLP：简单全连接网络，baseline模型
- CNN：捕获局部量价模式(如K线形态)
- RNN/LSTM：捕获时序依赖关系
- Transformer：自注意力机制捕获长程依赖

### Step 3: 训练策略
- 损失函数：IC Loss / ListNet排序损失
- 正则化：Dropout/L2/Early Stopping
- 数据增强：时序数据的噪声注入/时间扭曲
- 分布式训练：多GPU加速大规模模型

### Step 4: Alpha信号提取
- 模型输出→截面排序→Alpha信号
- 信号平滑：指数移动平均降低换手
- 信号组合：多模型信号的加权融合
- 归因分析：哪些输入特征贡献最大

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# 深度学习Alpha信号报告

## 一、模型架构
| 组件 | 配置 |
|------|------|

## 二、信号表现
[IC/多空收益/Sharpe]

## 三、当期Alpha信号
[Top/Bottom股票与信号强度]

## 四、归因分析
[特征贡献度、注意力权重]
```

### brief 风格（快速分析）
```
## DL Alpha速览
- Transformer模型，IC=0.05
- 多空年化 22%，Sharpe 2.1
- 本期强Alpha：[股票列表]
- 关键驱动：量价模式+资金流
```

参考 `references/deep-learning-alpha-guide.md` 获取详细方法论与 A股实证研究。
