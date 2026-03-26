---
name: a-share-shareholder-structure
description: A股股权结构/股东分析。当用户说"股权结构"、"股东"、"十大股东"、"十大流通股东"、"股东人数"、"筹码集中度"、"shareholder"、"XX的股东是谁"、"股东人数变化"、"解禁"、"限售"、"质押"时触发。分析企业股权结构（控股股东/实控人/机构持仓）、股东人数变化趋势（筹码集中度）、解禁压力、股权质押风险。支持研报风格（formal）和快速查看风格（brief）。
---

# A股股权结构/股东分析助手

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 十大股东（通过 efinance）
python -c "import efinance as ef; df=ef.stock.get_top10_stock_holder_info(stock_code='600519'); print(df.to_json(orient='records', force_ascii=False))"

# 十大流通股东（通过 efinance）
python -c "import efinance as ef; df=ef.stock.get_top10_stock_holder_info(stock_code='600519'); print(df[df['股东类型']=='流通'].to_json(orient='records', force_ascii=False))" 2>/dev/null || echo "从十大股东中筛选流通股东"

# 股东人数（通过 akshare）
python -c "import akshare as ak; df=ak.stock_zh_a_gdhs(symbol='600519'); print(df.to_json(orient='records', force_ascii=False))"

# 股权质押比例（通过 akshare，全市场数据）
python -c "import akshare as ak; df=ak.stock_gpzy_pledge_ratio_em(); print(df[df['股票代码']=='600519'].to_json(orient='records', force_ascii=False))"

# 个股行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]

# K线（看股东变化前后走势）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
```

补充：通过 web 搜索获取解禁日历、实控人信息、一致行动人关系、限售股解禁明细等。

## Workflow

### Step 1: 获取股权数据

获取十大股东 + 十大流通股东 + 股东人数历史 + 质押比例 + 个股行情。多只股票时并行获取。

### Step 2: 股权结构分析

- **控股股东/实控人**：识别最终控制人，穿透持股链条
- **机构持仓**：基金/社保/保险/QFII/北向资金占比
- **外资占比**：北向资金 + QFII 合计
- **股东类型分布**：国资/民企/外资/混合所有制
- **一致行动人**：识别关联方持股合计

> 详见 [references/shareholder-guide.md](references/shareholder-guide.md) 中的股东类型解读和分析框架。

### Step 3: 筹码集中度分析

- **股东人数变化趋势**：连续减少=筹码集中（利好信号），连续增加=筹码分散（利空信号）
- **户均持股变化**：总股本/股东人数，反映人均筹码量
- **机构占比变化**：机构增仓=专业资金看好
- **与股价走势对照**：股东人数减少但股价未涨=可能蓄势

### Step 4: 风险排查

- **质押风险**：质押率>50% 需重点警惕，关注平仓线
- **解禁压力**：未来6个月解禁规模（首发/定增/股权激励），解禁市值占流通市值比例
- **减持计划**：大股东是否已发布减持预告
- **股权纷争**：是否存在控制权争夺、举牌等情况

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 输出格式 | 完整股权结构分析报告 | 快速要点 |
| 股权结构 | 详细股东穿透图+持股比例表 | 仅列控股股东/实控人和关键机构 |
| 筹码分析 | 股东人数趋势图+户均持股表 | 仅标注集中or分散趋势 |
| 风险排查 | 质押/解禁/减持逐项详析 | 仅标注高风险项 |
| 结论 | 客观陈述（"控股股东持股X%，质押率X%"） | 可加简要判断 |

默认风格：brief。用户要求"详细分析"/"出报告"时用 formal。

## 关键规则

1. **数据滞后性**：十大股东数据来自季报/半年报/年报，最新数据可能滞后1-3个月，分析时注明报告期
2. **股东人数减少不等于一定涨**：筹码集中是必要条件非充分条件，需结合基本面和市场环境
3. **高质押=高风险**：质押率>50%需警惕，股价大跌可能触发平仓，形成负反馈
4. **解禁不等于一定卖**：解禁只是获得卖出权利，实际减持需看股东意愿和市场环境，但会形成心理压力
5. **举牌规则**：持股达5%需披露，每增减5%需再次披露，触发要约收购线为30%
6. **不做交易建议**：只分析股权结构和风险，不建议"买入/卖出"

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
