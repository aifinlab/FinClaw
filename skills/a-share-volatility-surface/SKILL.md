---
name: a-share-volatility-surface
description: A股波动率曲面/隐含波动率分析。当用户说"波动率曲面"、"隐含波动率"、"IV曲面"、"volatility surface"、"波动率微笑"、"波动率偏斜"、"IV skew"时触发。基于 cn-stock-data 获取数据，构建与分析波动率曲面。支持 formal/brief 两种输出风格。
---

# 波动率曲面/隐含波动率分析助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **期权数据**: 各行权价/到期日的期权价格
- **标的行情**: ETF/指数实时价格
- **历史IV**: 隐含波动率时序数据

## 分析工作流

### Step 1: 隐含波动率计算
- BSM模型反解IV：Newton-Raphson迭代
- 按行权价/到期日构建IV矩阵
- IV微笑/偏斜形态分析
- ATM IV作为市场波动率预期的核心指标

### Step 2: 波动率曲面构建
- 插值方法：SVI(Stochastic Volatility Inspired)参数化
- 时间维度：短期/中期/长期IV期限结构
- 行权价维度：OTM Put/ATM/OTM Call的IV差异
- 曲面平滑：消除套利机会的无套利约束

### Step 3: 曲面形态分析
- 偏斜度(skew)：OTM Put IV - OTM Call IV
- 凸度(convexity)：翼部IV相对ATM的凸起程度
- 期限结构斜率：远月IV vs 近月IV
- 曲面动态：曲面形态随标的价格变动的规律

### Step 4: 交易信号
- IV分位数：当前IV在历史中的位置
- IV vs RV：隐含波动率与已实现波动率的差(VRP)
- 偏斜异常：skew突变可能预示方向性行情
- 期限结构倒挂：近月IV>远月IV预示短期风险

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# [标的] 波动率曲面分析报告

## 一、IV概览
| 指标 | 数值 | 分位数 |
|------|------|--------|
| ATM IV | 22.5% | P55 |

## 二、曲面形态
[偏斜度、凸度、期限结构]

## 三、异常信号
[IV vs RV、偏斜异常]

## 四、交易建议
[基于曲面的期权策略]
```

### brief 风格（快速分析）
```
## [标的] IV速览
- ATM IV 22.5% (P55)，中等水平
- Skew -3.2%，正常偏斜
- VRP +2.1%，卖权有溢价
- 期限结构正常，无倒挂
```

参考 `references/volatility-surface-guide.md` 获取详细方法论与 A股实证研究。

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
