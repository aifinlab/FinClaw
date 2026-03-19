---
name: a-share-trade-classification
description: A股交易分类/Lee-Ready算法。当用户说"交易分类"、"Lee-Ready"、"买卖分类"、"主动买卖"、"trade classification"、"BVC"时触发。基于 cn-stock-data 获取数据，对成交进行买卖方向分类。支持 formal/brief 两种输出风格。
---

# 交易分类/Lee-Ready算法助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **逐笔成交**: 成交价格/数量/时间
- **盘口数据**: 成交时的买卖报价
- **BSFlag**: A股自带的买卖标志(如有)

## 分析工作流

### Step 1: 分类算法
- Quote Rule：成交价>中间价→买入，<中间价→卖出
- Tick Rule：成交价>上一笔→买入(uptick)，<上一笔→卖出
- Lee-Ready：先用Quote Rule，平局时用Tick Rule
- BVC(Bulk Volume Classification)：基于价格变动的批量分类

### Step 2: A股数据处理
- 深交所逐笔数据自带BSFlag，可直接使用
- 上交所需要用Lee-Ready算法推断
- 集合竞价成交的分类：通常标记为中性
- 大宗交易的分类：单独处理

### Step 3: 分类质量评估
- 准确率：与真实BSFlag对比(深交所可验证)
- Lee-Ready在A股的准确率约85-90%
- Tick Rule在A股的准确率约75-80%
- BVC方法准确率较低但计算简单

### Step 4: 分类结果应用
- 净买入量 = 主动买入量 - 主动卖出量
- 订单流不平衡(OFI)：预测短期价格方向
- VPIN计算：基于买卖分类的波动率预测
- 大单方向分析：大单的买卖方向统计

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# [标的] 交易分类分析报告

## 一、分类结果
| 时段 | 主动买(万股) | 主动卖(万股) | 净买入 |
|------|------------|------------|--------|

## 二、分类方法
[使用的算法与准确率]

## 三、订单流分析
[OFI、净买入趋势]

## 四、信号解读
```

### brief 风格（快速分析）
```
## [标的] 交易分类速览
- 主动买入 58%，主动卖出 42%
- 净买入 +1,200万股
- 大单(>10万)净买入 +350万股
- 信号：资金偏多头
```

参考 `references/trade-classification-guide.md` 获取详细方法论与 A股实证研究。
