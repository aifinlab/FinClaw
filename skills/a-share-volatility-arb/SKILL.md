---
name: a-share-volatility-arb
description: A股波动率套利/Vega交易策略。当用户说"波动率套利"、"vol arb"、"Vega交易"、"做多波动率"、"做空波动率"、"波动率交易"、"straddle"、"strangle"时触发。基于 cn-stock-data 获取数据，设计波动率套利策略。支持 formal/brief 两种输出风格。
---

# 波动率套利/Vega交易助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **期权数据**: 各合约价格与IV
- **标的行情**: 实时价格与历史波动率
- **VIX类指标**: 中国波指/iVIX

## 分析工作流

### Step 1: 波动率定价判断
- IV vs HV(历史波动率)：IV偏高→卖波动率
- IV分位数：当前IV在历史中的位置
- VRP(方差风险溢价) = IV² - RV²
- 波动率期限结构：近月vs远月IV关系

### Step 2: 策略构建
- 做多波动率：买入Straddle/Strangle
- 做空波动率：卖出Straddle/Iron Condor
- 波动率价差：买近月卖远月(或反向)
- 偏斜交易：买低IV行权价卖高IV行权价

### Step 3: Delta对冲
- 建仓时Delta中性：调整期权比例
- 动态对冲：标的价格变动时重新对冲
- 对冲频率：日度/实时，平衡成本与风险
- Gamma scalping：利用Gamma正值赚取对冲收益

### Step 4: 风险管理
- 最大亏损控制：设置止损线
- Vega敞口限制：控制波动率风险暴露
- 到期风险：临近到期Gamma风险急剧增大
- 黑天鹅防护：保留少量OTM期权作为保险

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# 波动率套利策略报告

## 一、波动率评估
| 指标 | 数值 | 信号 |
|------|------|------|

## 二、策略方案
[具体期权组合、Greeks]

## 三、对冲计划
[Delta对冲方案、频率]

## 四、风险控制
[止损、最大亏损]
```

### brief 风格（快速分析）
```
## 波动率套利速览
- IV 25% vs HV 20%，IV偏高
- 建议：卖出Straddle，收取权利金
- Delta对冲：日度调整
- 最大亏损控制在权利金的150%
```

参考 `references/volatility-arb-guide.md` 获取详细方法论与 A股实证研究。

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
