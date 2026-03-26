---
name: a-share-cash-flow
description: A股现金流分析/自由现金流质量评估。当用户说"现金流"、"自由现金流"、"FCF"、"cash flow"、"经营现金流"、"XX的现金流怎么样"、"收现比"、"净现比"、"资本开支"、"现金流量表"、"现金流分析"、"现金流质量"时触发。MUST USE when user asks about cash flow analysis, free cash flow (FCF), operating cash flow quality, or cash conversion ratio. 深度分析企业三大现金流（经营/投资/筹资）质量，计算自由现金流，评估盈利含金量和资本配置效率。支持研报风格（formal）和快速分析风格（brief）。
---

# A 股现金流分析

## 重要：数据时效性

**训练数据中的财务数据已过期。** 每次执行时必须：
1. 通过 cn-stock-data 获取最新财务指标
2. 通过 web 搜索确认最新财报发布日期和现金流相关披露
3. 如果搜索不到最新财报，明确告知用户"未找到最新XX季/年报"，不要用旧数据编造

## 数据源

### 必需数据（通过 cn-stock-data）
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 财务指标（含现金流量表核心字段）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]

# 近 2 年日线行情（分析股价走势 vs 现金流趋势）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [2年前日期]

# 实时行情（当前市值，用于计算 FCF Yield）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
```

### 补充数据（通过 web 搜索）
- 搜索 "[公司名] 资本开支 计划" 获取 capex guidance
- 搜索 "[公司名] 分红 政策 股息" 获取分红/回购信息
- 搜索 "[公司名] 现金流 分析" 获取券商/媒体对现金流的点评
- 搜索 "[公司名] 应收账款 存货" 获取营运资本变动线索

## Workflow

详见 `references/cash-flow-guide.md` 的分析框架和判断标准。

### Phase 1: 数据收集
- 运行 cn-stock-data 获取近 4-8 期财务数据（至少覆盖 2 个完整财年）
- Web 搜索资本开支计划、分红政策、现金流相关公告
- 确认数据完整性，缺失部分标注"数据暂缺"

### Phase 2: 经营现金流分析
参见 `references/cash-flow-guide.md` 的指标解读规则。
- **收现比** = 销售商品收到的现金 / 营业收入（>1 为优，说明回款好）
- **净现比** = 经营活动现金流净额 / 净利润（>1 为优，说明利润含金量高）
- 经营现金流趋势：是否持续增长，是否与净利润同向变动
- 营运资本变动：应收/存货/应付对经营现金流的影响

### Phase 3: 投资现金流分析
- **资本开支**（购建固定资产+无形资产支出）：占营收比例、增长趋势
- 并购支出：取得子公司支付的现金
- 资产处置：处置固定资产/子公司收到的现金
- 投资收益：是否依赖理财/投资收益美化利润

### Phase 4: 自由现金流计算与质量评估
- **FCF = 经营活动现金流净额 - 资本开支**
- **FCF Yield = FCF / 市值**（与国债收益率比较）
- FCF 趋势：近 4-8 期是否持续为正、是否增长
- FCF 转化率 = FCF / 净利润（衡量利润最终能变成多少真金白银）
- 筹资现金流：分红/回购 vs 借债/增发，资本配置是否合理

### Phase 5: 报告生成
根据用户风格要求选择输出格式。
- formal: 完整现金流分析报告（6-10 页）
- brief: Markdown 快速分析（1-2 页）
- 默认风格: **brief**

## 风格说明

| 维度 | formal（研报风格） | brief（快速分析） |
|------|-------------------|------------------|
| 篇幅 | 6-10 页 .docx | 1-2 页 Markdown |
| 标题 | "[公司名]([代码])现金流质量深度分析" | "XX 现金流速评" |
| 结构 | 核心结论→经营CF分析→投资CF分析→FCF评估→资本配置→风险提示→附表 | 关键指标→现金流画像→FCF→风险点 |
| 图表 | 4-6 个（三大CF趋势、收现比/净现比、FCF、capex占比） | 关键数据表 1 个 |
| 引用 | 必须标注数据来源 | 可省略 |
| 免责声明 | 需要 | 不需要 |

## QC 验证
- 所有现金流数字必须与 cn-stock-data 返回一致
- 收现比/净现比/FCF 计算必须手动复核
- 不允许出现"预计"、"大约"等模糊表述（除引用分析师观点外）
- 关注现金流与利润背离的情况，必须给出解释
- 行业特征必须纳入考量（重资产 vs 轻资产，周期 vs 消费）

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
