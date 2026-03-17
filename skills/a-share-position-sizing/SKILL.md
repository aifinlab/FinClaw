---
name: a-share-position-sizing
description: A股仓位管理/凯利公式/仓位计算。当用户说"仓位"、"position sizing"、"该买多少"、"仓位管理"、"凯利公式"、"Kelly"、"加仓"、"减仓"时触发。基于 cn-stock-data 获取数据，量化计算最优仓位。支持研报风格（formal）和快速分析风格（brief）。
---

# A股仓位管理/凯利公式/仓位计算

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取标的数据
获取标的K线 + 波动率 + 基本面数据。

### Step 2: 风险度量
- 个股波动率（20日/60日年化波动率）
- ATR（真实波幅）
- 下行风险（半方差/CVaR）

### Step 3: 仓位计算
- **等风险贡献**：w = k / σ_i（波动率倒数加权）
- **凯利公式**：f* = (p × b - q) / b（p=胜率, b=盈亏比, q=1-p）
- **ATR仓位法**：仓位 = 风险预算 / (N × ATR)
- **固定风险法**：仓位 = 可承受亏损 / 止损距离

### Step 4: 约束条件
- 单只个股 < 总资金的 20%
- 单行业 < 总资金的 30%
- 总仓位根据市场状态调整（牛市80-100%，震荡50-80%，熊市20-50%）

### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 仓位计算 | 多方法对比 | 建议仓位 |
| 风险分析 | 波动率+VaR | 风险等级 |
| 加减仓计划 | 分批建仓方案 | 单次建议 |

默认风格：brief。

## 关键规则
1. 仓位管理比选股更重要——错误的仓位可以毁掉正确的选股
2. 永远不要满仓单只股票
3. 凯利公式的实际应用应使用半凯利（f*/2）更稳健
4. A 股 T+1 制度下，仓位调整需提前一天规划
5. 市场状态是仓位的宏观约束——熊市轻仓是第一原则
