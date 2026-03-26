---
name: a-share-pairs-trading
description: A股配对交易/统计套利分析。当用户说"配对交易"、"pairs trading"、"统计套利"、"价差交易"、"XX和YY能配对吗"、"协整"、"spread"、"套利"时触发。基于 cn-stock-data 获取双标的K线数据，进行协整检验、价差分析、交易信号生成。支持研报风格（formal）和快速分析风格（brief）。
---

# A股配对交易分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
# 两只股票的K线
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE1] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE2] --freq daily --start [日期]
# 行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2]
```

**量化计算**：
```bash
QSCRIPTS="$SKILLS_ROOT/a-share-pairs-trading/scripts"
python "$QSCRIPTS/pairs_analyzer.py" --stock1 data1.json --stock2 data2.json --window 60
```

## Workflow

### Step 1: 选择配对标的
- 同行业/同概念板块优先（基本面相似性）
- 历史价格相关性 > 0.8 作为初筛条件

### Step 2: 协整检验
1. ADF 检验两个价格序列的平稳性（应为 I(1)）
2. Engle-Granger 两步法：OLS 回归 → 残差 ADF 检验
3. p-value < 0.05 认为存在协整关系

### Step 3: 价差序列构建
- 方法 A：对数价格比 ln(P1/P2)
- 方法 B：OLS 残差法 P1 - β×P2 - α
- 计算 Z-score = (spread - mean) / std

### Step 4: 交易信号
- 开多价差：Z-score < -2（价差偏低）
- 开空价差：Z-score > +2（价差偏高）
- 平仓：Z-score 回归至 0 附近（±0.5）
- 止损：Z-score 超过 ±3

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 协整检验 | 完整统计量+p值 | 结论（是/否） |
| 价差分析 | 时序图+分布 | 当前 Z-score |
| 回测 | 完整绩效指标 | 年化收益+夏普 |
| 半衰期 | OU 模型详细 | 天数 |

默认风格：brief。

## 关键规则
1. A 股 T+1 限制：当日买入次日才能卖出，配对交易需考虑此约束
2. 涨跌停：一方涨停另一方未涨停会导致价差异常扩大
3. 停牌风险：一方停牌导致无法对冲
4. 协整关系可能失效——需定期检验，建议滚动窗口
5. 交易成本：双边交易成本约 0.2%，需纳入回测

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
