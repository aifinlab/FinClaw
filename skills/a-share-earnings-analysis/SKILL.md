---
name: a-share-earnings-analysis
description: A股个股财报分析/业绩点评。当用户说"财报分析"、"季报解读"、"年报分析"、"业绩点评"、"XX的财报怎么样"、"earnings analysis"时触发。从 cn-stock-data 获取财务指标和行情数据，结合 web 搜索获取财报公告原文和市场预期，生成结构化财报分析报告。支持券商业绩点评风格（formal, 8-12页 .docx）和个人分析笔记风格（brief, 1-2页 Markdown）。不适用于晨会纪要（用 a-share-morning-note）或选股筛选（用 a-share-stock-screen）。
---

# A 股财报分析

## 重要：数据时效性

**训练数据中的财务数据已过期。** 每次执行时必须：
1. 通过 cn-stock-data 获取最新财务指标
2. 通过 web 搜索确认最新财报发布日期和内容
3. 如果搜索不到最新财报，明确告知用户"未找到最新XX季/年报"，不要用旧数据编造

## 数据源

### 必需数据（通过 cn-stock-data）
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 财务指标（adata 43 字段）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]

# 近 6 个月日线行情（分析股价走势 vs 业绩）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [6个月前日期]

# 近 30 日资金流向
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE] --days 30

# 实时行情（当前估值水平）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
```

### 补充数据（通过 web 搜索）
- 搜索 "[公司名] [年份] [季度]报 业绩" 获取财报公告
- 搜索 "[公司名] 业绩 分析师 预期" 获取市场一致预期
- 搜索 "[公司名] 管理层 业绩说明会" 获取管理层点评

## Workflow

详见 `references/workflow.md` 的 5 阶段分步指引。

### Phase 1: 数据收集
- 运行 cn-stock-data 获取财务/行情/资金流数据
- Web 搜索财报公告原文、业绩预告、分析师点评
- 确认数据完整性，缺失部分标注"数据暂缺"

### Phase 2: 核心分析
参见 `references/financial-metrics.md` 的指标解读规则。
- 营收分析：规模、增速（YoY/QoQ）、收入结构变化
- 盈利分析：净利润、扣非净利润、毛利率、净利率变化趋势
- 现金流：经营性现金流 vs 净利润匹配度
- 资产质量：应收账款周转、存货周转、资产负债率
- 估值水平：PE/PB 当前分位 vs 历史区间

### Phase 3: 综合判断
- 业绩超预期/符合预期/低于预期
- 核心亮点（2-3个）
- 核心风险（2-3个）
- 估值合理性

### Phase 4: 报告生成
根据用户风格要求选择模板，参见 `references/report-structure.md`。
- formal: 完整 .docx 报告（8-12 页）
- brief: Markdown 笔记（1-2 页）

### Phase 5: QC 验证
- 所有财务数字必须与 cn-stock-data 返回一致
- 同比/环比计算必须手动复核
- 不允许出现"预计"、"大约"等模糊表述（除引用分析师观点外）
- 检查报告日期是否正确

## 风格说明

| 维度 | formal（券商业绩点评） | brief（个人分析笔记） |
|------|---------------------|---------------------|
| 篇幅 | 8-12 页 .docx | 1-2 页 Markdown |
| 标题 | "[公司名]([代码])YYYY年Q[X]业绩点评" | "XX Q[X] 财报笔记" |
| 结构 | 投资要点→财务分析→估值→风险→附表 | 关键数字→亮点→风险→个人判断 |
| 图表 | 4-6 个（营收趋势、利润趋势、ROE、PE Band） | 关键数据表 1 个 |
| 引用 | 必须标注数据来源 | 可省略 |
| 免责声明 | 需要 | 不需要 |
| 投资评级 | 不给（避免合规风险） | 可给个人判断 |
