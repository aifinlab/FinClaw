---
name: a-share-var-analysis
description: A股VaR风险价值/条件VaR分析。当用户说"VaR"、"风险价值"、"value at risk"、"CVaR"、"ES"、"预期损失"、"最大可能亏多少"时触发。量化计算组合VaR和CVaR。支持formal和brief风格。
---

# A股VaR风险价值/条件VaR分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取收益率序列
### Step 2: 计算VaR
- 历史模拟法：收益率排序取分位数
- 参数法：假设正态分布，VaR = μ - z_α × σ
- Monte Carlo模拟：模拟10000条路径
### Step 3: 计算CVaR(ES)
CVaR = E[Loss | Loss > VaR]，尾部平均损失
### Step 4: 压力测试
用历史极端情景（2008/2015/2020）测算极端VaR
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| VaR | 多方法对比+置信度 | 95%VaR |
| CVaR | 尾部风险分析 | CVaR值 |
| 压力测试 | 历史情景分析 | 无 |
默认风格：brief。

## 关键规则
1. VaR 只回答正常情况下的最大损失——尾部风险需用CVaR
2. 历史模拟法最直观但依赖历史数据充分性
3. 参数法假设正态分布——A股收益率尖峰肥尾，会低估风险
4. 持有期不同VaR差异巨大——日VaR × √T ≈ T日VaR（近似）
5. 回测VaR：实际突破次数应接近理论水平

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
