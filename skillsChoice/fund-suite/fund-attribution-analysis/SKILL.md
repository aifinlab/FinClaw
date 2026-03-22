---
name: fund-attribution-analysis
description: |
  基金收益归因分析 - Brinson模型、因子归因、风格分析工具。
  当用户需要分析基金超额收益来源、进行业绩归因、评估基金经理能力时使用此技能。
  支持Brinson归因、因子归因、风格归因、行业归因、选股能力分析。
  触发关键词：收益归因、Brinson、业绩归因、超额收益、阿尔法归因、因子分析。
---

# 基金收益归因分析 (Fund Attribution Analysis)

基于Brinson模型和因子模型的基金收益归因分析工具。

## 功能概述

- **Brinson归因**: 资产配置效应、个股选择效应、交互效应
- **因子归因**: 市场因子、价值因子、动量因子、规模因子等
- **风格归因**: 成长/价值、大盘/小盘风格暴露
- **行业归因**: 行业配置贡献、行业内选股贡献
- **选股能力分析**: 超额收益分解、信息比率、择时能力

## 使用方法

### 命令行调用

```bash
# Brinson归因分析
fund-attribution --portfolio portfolio.json --benchmark 000300 --period 2024Q1

# 因子归因
fund-attribution --fund 000001 --factors value,momentum,size

# 风格分析
fund-attribution --style --fund 000001
```

### Python API

```python
from fund_attribution_analysis import AttributionAnalyzer

analyzer = AttributionAnalyzer()

# Brinson归因
result = analyzer.brinson_attribution(
    portfolio_returns=pf_returns,
    benchmark_returns=bm_returns,
    portfolio_weights=pf_weights,
    benchmark_weights=bm_weights
)

# 因子归因
result = analyzer.factor_attribution(
    fund_code='000001',
    factors=['value', 'momentum', 'size']
)
```

## Brinson归因模型

### 经典Brinson模型

将超额收益分解为三个部分：

```
超额收益 = 资产配置效应 + 个股选择效应 + 交互效应

R_p - R_b = Σ(w_pi - w_bi) × R_bi  [资产配置]
          + Σw_bi × (R_pi - R_bi)    [个股选择]
          + Σ(w_pi - w_bi) × (R_pi - R_bi) [交互效应]
```

其中：
- w_pi: 组合中资产i的权重
- w_bi: 基准中资产i的权重
- R_pi: 组合中资产i的收益
- R_bi: 基准中资产i的收益

### 多期Brinson归因

```
几何归因:
(1 + R_p) / (1 + R_b) - 1 = 配置贡献 + 选择贡献 + 交互贡献

对数归因:
ln(1 + R_p) - ln(1 + R_b) = 配置效应 + 选择效应
```

## 因子归因模型

### 常见因子

| 因子 | 定义 | 计算方式 |
|:---|:---|:---|
| 市场(MKT) | 市场风险暴露 | 市场组合收益 - 无风险利率 |
| 价值(HML) | 高减低价值因子 | 高BP组合收益 - 低BP组合收益 |
| 规模(SMB) | 小减大规模因子 | 小市值组合收益 - 大市值组合收益 |
| 动量(MOM) | 动量因子 | 过去12月高收益 - 过去12月低收益 |
| 质量(QUAL) | 质量因子 | 高ROE - 低ROE |
| 低波(LOWV) | 低波动因子 | 低波动组合 - 高波动组合 |

### 因子归因公式

```
R_p - R_f = α + β₁ × MKT + β₂ × HML + β₃ × SMB + β₄ × MOM + ε

解释度 = 1 - Var(ε) / Var(R_p)
```

## 输出格式

### Brinson归因报告

```json
{
  "attribution_id": "ATTR_20260321_001",
  "fund_code": "000001",
  "fund_name": "华夏成长混合",
  "period": "2024Q1",
  "analysis_date": "2026-03-21",
  "returns": {
    "portfolio": 0.085,
    "benchmark": 0.062,
    "excess": 0.023
  },
  "brinson_attribution": {
    "allocation_effect": 0.008,
    "selection_effect": 0.012,
    "interaction_effect": 0.003,
    "total_excess": 0.023
  },
  "sector_attribution": [
    {
      "sector": "科技",
      "portfolio_weight": 0.25,
      "benchmark_weight": 0.15,
      "portfolio_return": 0.12,
      "benchmark_return": 0.08,
      "allocation_effect": 0.004,
      "selection_effect": 0.010,
      "interaction_effect": 0.002
    }
  ],
  "conclusion": "超额收益主要来自选股能力，行业配置贡献较小"
}
```

## 示例

### 示例1: Brinson归因分析

**输入**:
```
分析基金000001相对于沪深300的Brinson归因
```

**输出**:
```
📊 Brinson归因分析报告

基金: 华夏成长混合 (000001)
对比基准: 沪深300指数 (000300)
分析区间: 2024Q1 (2024-01-01 ~ 2024-03-31)

收益表现:
  组合收益: 8.5%
  基准收益: 6.2%
  超额收益: 2.3% ✅

归因分解:
  资产配置效应: +0.8% (贡献35%)
  个股选择效应: +1.2% (贡献52%) ⭐
  交互效应:      +0.3% (贡献13%)
  ─────────────────────────────
  合计超额收益:  +2.3%

行业归因:
  科技:
    超配 +10% × 基准收益8% = 配置贡献 +0.8%
    组合收益12% - 基准8% = 选股贡献 +0.6%
  
  金融:
    低配 -5% × 基准收益4% = 配置贡献 -0.2%
    组合收益3% - 基准4% = 选股贡献 -0.1%

结论:
  ✅ 基金经理选股能力突出
  ✅ 科技行业超配和选股均有正贡献
  ⚠️ 金融板块低配虽减少拖累但选股偏弱
```

### 示例2: 因子归因分析

**输入**:
```
分析基金的风格因子暴露
```

**输出**:
```
📊 因子归因分析报告

基金: 华夏成长混合 (000001)
分析区间: 2023-03-21 ~ 2026-03-21 (3年)

因子暴露:
              暴露系数    t值      显著性
  市场因子:    0.92      15.2     ***
  价值因子:   -0.35      -4.8     ***  (偏向成长)
  规模因子:    0.28       3.2      **   (偏向小盘)
  动量因子:    0.15       2.1      *    (有动量暴露)
  质量因子:    0.42       5.6      ***

解释度: R² = 0.87 (模型解释87%的收益波动)

阿尔法: α = 2.3% (年化)
  → 剔除因子暴露后的纯主动收益
  → 信息比率: 0.85

风格画像:
  成长型小盘质量股
  偏好: 高成长 + 小市值 + 高质量
  回避: 低估值价值股

风险提示:
  ⚠️ 成长风格暴露较高，风格切换时波动大
  ⚠️ 小盘暴露可能面临流动性风险
```

## 注意事项

1. Brinson归因假设组合和基准成分已知
2. 多期归因建议使用几何归因法
3. 因子归因需要足够长的时间序列（建议2年以上）
4. 归因结果受基准选择影响较大
5. 交互效应通常较小，可合并到选股效应
6. 注意区分运气和能力（需要多年数据验证）

## 依赖

```
numpy>=1.20.0
pandas>=1.3.0
scipy>=1.7.0
statsmodels>=0.13.0
```

## 作者

FinClaw - 上海财经大学金融研究工具
