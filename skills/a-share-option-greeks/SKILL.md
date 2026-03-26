---
name: a-share-option-greeks
description: A股期权Greeks/风险敞口分析。当用户说"Greeks"、"Delta"、"Gamma"、"Theta"、"Vega"、"期权风险"、"希腊字母"、"期权敞口"时触发。基于 cn-stock-data 获取数据，计算与分析期权Greeks。支持 formal/brief 两种输出风格。
---

# 期权Greeks/风险敞口分析助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **期权数据**: 期权价格/行权价/到期日
- **标的行情**: 实时价格与波动率
- **利率数据**: 无风险利率

## 分析工作流

### Step 1: Greeks计算
- Delta：期权价格对标的价格的敏感度
- Gamma：Delta对标的价格的敏感度(二阶)
- Theta：期权价格对时间的敏感度(时间衰减)
- Vega：期权价格对波动率的敏感度

### Step 2: 组合Greeks汇总
- 组合Delta：所有持仓的Delta加总
- 组合Gamma：Gamma风险暴露
- 组合Theta：每日时间价值损耗
- 组合Vega：波动率变动的盈亏

### Step 3: Greeks动态分析
- Delta随标的价格变化的曲线(Delta profile)
- Gamma集中区域：ATM附近Gamma最大
- Theta加速：临近到期时间价值加速衰减
- Vega期限结构：远月Vega大于近月

### Step 4: 风险管理应用
- Delta对冲：保持组合Delta中性
- Gamma scalping：利用Gamma正值做日内对冲
- Theta收割：卖出期权赚取时间价值
- Vega交易：做多/做空波动率

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# [标的] 期权Greeks分析报告

## 一、Greeks概览
| Greek | 数值 | 含义 |
|-------|------|------|

## 二、组合敞口
[组合Greeks汇总]

## 三、情景分析
[标的±5%/IV±5%的盈亏]

## 四、对冲建议
[Delta对冲方案]
```

### brief 风格（快速分析）
```
## [标的] Greeks速览
- Delta +0.45，偏多头
- Gamma +0.08，ATM附近
- Theta -15元/天
- Vega +120元/1%IV
- 建议：卖出1手近月平值对冲Delta
```

参考 `references/option-greeks-guide.md` 获取详细方法论与 A股实证研究。

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
