---
name: a-share-factor-analysis
description: A股单因子研究/IC检验。当用户说"因子分析"、"单因子"、"IC"、"IR"、"因子检验"、"factor analysis"、"因子有效性"、"XX因子表现怎么样"、"因子IC"、"因子收益"、"因子衰减"、"quintile分析"时触发。基于 cn-stock-data 获取股票池行情与财务数据，通过 factor_analyzer.py 计算 IC/IR、分位组合收益、因子换手率等量化指标。支持专业因子研究报告风格（formal）和快速因子检验风格（brief）。不适用于多因子组合优化（需自建模型）或个股基本面分析（用 a-share-earnings-analysis）。
---

# A 股单因子研究 / IC 检验

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
ANALYZER="$SKILLS_ROOT/a-share-factor-analysis/scripts/factor_analyzer.py"

# 获取股票池行情（如沪深300成分股）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE1],[CODE2],... --freq daily --start [回测起始日期]

# 获取财务指标（PE/PB/ROE 等因子原始值）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE1],[CODE2],...

# 获取实时行情（市值、PE、PB）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],...

# 运行因子分析
python "$ANALYZER" --factor [FACTOR] --period [N] --data [input.json]
```

## Workflow

### Step 1: 确定研究范围
1. 明确因子名称（PE/PB/ROE/动量/波动率/换手率等）
2. 确定股票池（沪深300/中证500/全A等，默认沪深300）
3. 确定回测区间（默认近3年）和调仓周期（默认20个交易日）

### Step 2: 数据获取与因子构建
1. 获取股票池所有成分股的日线 kline 数据
2. 获取 finance/quote 数据构建因子截面值
3. 整理为 factor_analyzer.py 所需的 JSON 格式（参见 references/factor-analysis-guide.md）

### Step 3: 运行因子分析
调用 `factor_analyzer.py` 计算：
- **IC 序列**：每期因子值与下期收益的 Rank IC（Spearman 相关系数）
- **IR**：IC 均值 / IC 标准差，衡量因子稳定性
- **分位组合**：按因子值分5组，比较各组平均收益
- **因子换手率**：相邻两期 Top/Bottom 组合的持仓变化比例
- **因子衰减**：不同持仓周期下 IC 的衰减速度

### Step 4: 结果解读
参见 `references/factor-analysis-guide.md` 的解读标准：
- IC 均值 > 0.03 且 IR > 0.5 → 因子有效
- 分位组合单调性 → 因子区分度
- 换手率过高 → 实际可执行性存疑

### Step 5: 输出

## 风格说明

| 维度 | formal（专业因子研究报告） | brief（快速因子检验） |
|------|--------------------------|---------------------|
| 篇幅 | 2-4 页 | 半页 |
| IC 分析 | IC 序列图描述 + 分布统计 + 显著性检验 | IC 均值 + IR 一行结论 |
| 分位分析 | 五分位组合收益表 + 多空收益曲线描述 | Top-Bottom 收益差 |
| 因子衰减 | 多周期 IC 衰减表 | 最优持仓周期 |
| 换手率 | 月度换手率序列 | 平均换手率 |
| 结论 | 因子有效性评级 + 使用建议 + 局限性 | 有效/无效 + 一句话建议 |
| 免责声明 | 需要（历史回测不代表未来表现） | 不需要 |

## 关键规则

1. **Rank IC 优先于 Pearson IC**：A 股因子值分布偏态严重，必须用 Spearman 秩相关
2. **去极值与中性化**：分析前对因子值做 MAD 去极值，formal 模式需做市值/行业中性化
3. **存活偏差**：说明是否剔除退市股，ST 股必须剔除
4. **交易成本**：分位组合收益需说明是否扣除交易成本（双边千三估算）
5. **数据来源标注**：标明因子原始数据来自 cn-stock-data 的哪个接口
6. **A 股特色因子**：关注涨跌停、ST、壳价值等 A 股特有因素对因子的影响
