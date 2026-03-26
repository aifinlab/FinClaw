---
name: a-share-informed-trading
description: A股知情交易/PIN模型分析。当用户说"知情交易"、"PIN"、"informed trading"、"内幕交易"、"信息交易"、"知情交易概率"时触发。基于 cn-stock-data 获取数据，估算知情交易概率。支持 formal/brief 两种输出风格。
---

# 知情交易/PIN模型分析助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **逐笔成交**: 买卖主导分类
- **盘口数据**: 委托到达率
- **事件数据**: 公告/财报日期

## 分析工作流

### Step 1: PIN模型估计
- 参数：α(信息事件概率)、δ(坏消息概率)、μ(知情交易到达率)、ε_b/ε_s(非知情买卖到达率)
- 似然函数：基于每日买卖主导订单数
- PIN = αμ / (αμ + ε_b + ε_s)
- MLE估计：最大化对数似然函数

### Step 2: VPIN估计
- Volume-synchronized PIN：不需要MLE
- 将成交量等分为bucket
- 每个bucket用BVC分类买卖
- VPIN = Σ|V_buy - V_sell| / (N × V_bucket)

### Step 3: 知情交易事件分析
- 公告前PIN变化：PIN上升可能预示信息泄露
- 财报前后PIN对比：信息不对称的变化
- 大宗交易前PIN：是否存在提前知情
- 监管事件：立案调查前的异常交易

### Step 4: 应用与解读
- PIN高的股票：信息不对称大，价差宽
- PIN作为因子：高PIN股票可能有更高的风险溢价
- PIN预警：PIN突然上升可能预示重大事件
- 合规监控：异常PIN可作为内幕交易线索

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# [标的] 知情交易分析报告

## 一、PIN估计
| 参数 | 数值 |
|------|------|
| PIN | 0.15 |

## 二、VPIN监控
[VPIN时序与预警]

## 三、事件分析
[公告前后PIN变化]

## 四、风险提示
```

### brief 风格（快速分析）
```
## [标的] 知情交易速览
- PIN = 0.15，知情交易概率中等
- VPIN近期稳定，无异常
- 近期无公告前PIN异常上升
- 信息不对称程度：正常
```

参考 `references/informed-trading-guide.md` 获取详细方法论与 A股实证研究。

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
