---
name: a-share-index-enhance
description: A股指数增强策略/超额收益分析。当用户说"指数增强"、"index enhance"、"超额收益"、"跑赢指数"、"增强策略"、"alpha"、"怎么跑赢沪深300"时触发。基于 cn-stock-data 获取指数成分股数据，量化构建指数增强组合。支持研报风格（formal）和快速分析风格（brief）。
---

# A股指数增强策略

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [INDEX_CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE1],[CODE2],...
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],...
```

## Workflow

### Step 1: 确定基准指数
沪深300(SH000300) / 中证500(SH000905) / 中证1000(SH000852)

### Step 2: 获取成分股数据
获取指数成分股列表、权重、K线数据、财务指标。

### Step 3: 构建增强因子
- **价值因子**：EP、BP、DP（高于基准均值的股票超配）
- **质量因子**：ROE、毛利率、现金流稳定性
- **动量因子**：过去20日收益率（去除最近5日）
- **低波因子**：过去60日波动率（低波超配）

### Step 4: 偏离度控制
- 行业偏离 < ±3%（相对基准权重）
- 个股偏离 < ±1%
- 风格因子暴露中性化
- 换手率约束：月度换手 < 30%

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 因子构成 | 多因子权重 + IC/IR | 主要alpha来源 |
| 组合构建 | 完整超配/低配名单 | Top 10 超配 |
| 跟踪误差 | TE 目标 + 信息比率 | 预期超额 |

默认风格：brief。

## 关键规则
1. 指数增强的核心是控制跟踪误差（TE < 5%年化）
2. 行业中性是底线——避免行业偏离贡献过多超额
3. A 股特殊：ST/涨跌停/停牌股需特殊处理
4. 交易成本显著影响超额——换手率控制很重要
5. 成分股调整日（6月/12月）需注意调仓冲击

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
