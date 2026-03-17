# 财报分析 Workflow 详细步骤

## Phase 1: 数据收集（必须先完成）

### Step 1.1: 确认分析标的
- 解析用户提到的公司名或代码
- 通过 cn-stock-data quote 确认代码正确、公司存在
- 确认用户想分析的是哪一期财报（最新季报？年报？）

### Step 1.2: 获取财务数据
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
从返回的 43 字段中提取关键指标：
- 每股指标：basic_eps, diluted_eps, net_asset_ps, oper_cf_ps
- 盈利能力：roe_wtd, roa_wtd, gross_margin, net_margin
- 成长性：total_rev_yoy_gr, net_profit_yoy_gr
- 偿债能力：curr_ratio, quick_ratio, asset_liab_ratio
- 运营效率：total_asset_turn_days, inv_turn_days, acct_recv_turn_days

### Step 1.3: 获取行情数据
```bash
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [6个月前]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE] --days 30
```

### Step 1.4: Web 搜索补充
搜索以下关键词（按顺序尝试）：
1. "[公司名] [年度] 年报/季报"
2. "[公司名] 业绩快报"
3. "[证券代码] 业绩预告"
4. "[公司名] 分析师 目标价"

**红旗检查**：
- 如果搜索结果中的财报日期超过 3 个月前，提醒用户"最新财报可能尚未发布"
- 如果财务数据与公告内容不一致，以公告为准并标注差异

## Phase 2: 核心分析

### Step 2.1: 营收分析
- 总收入金额及同比增速
- 分业务/产品线收入（如能从公告获取）
- 收入质量：是否依赖非经常性收入

### Step 2.2: 盈利分析
- 净利润 vs 扣非净利润（差额大说明有非经常性损益）
- 毛利率变化趋势（连续 4-8 个季度）
- 净利率变化趋势
- 三费（销售/管理/财务费用）占比变化

### Step 2.3: 现金流分析
- 经营性现金流 / 净利润 比率（健康值 > 0.8）
- 自由现金流 = 经营现金流 - 资本支出
- 应收账款周转天数变化（上升=回款变慢=警惕）

### Step 2.4: 资产质量
- 存货周转天数变化
- 商誉规模及占净资产比例（商誉 > 30% 净资产需警示）
- 有息负债率

### Step 2.5: 估值水平
- 当前 PE / PB
- PE 历史分位（需要历史 K 线+EPS 计算）
- 与行业平均估值对比（如有可比公司数据）

## Phase 3: 综合判断

### Step 3.1: 业绩定性
- 超预期：实际净利润 > 市场一致预期 10%+
- 符合预期：差异在 ±10% 以内
- 低于预期：实际净利润 < 一致预期 10%+
- 如无一致预期数据，与去年同期和上季度对比

### Step 3.2: 核心亮点（限 2-3 个）
提炼最重要的正面变化，用数字支撑。

### Step 3.3: 核心风险（限 2-3 个）
提炼最需关注的风险点，用数字支撑。

## Phase 4: 报告生成

参见 `report-structure.md` 选择对应风格模板。

**必须遵守的规则**：
- 财务数字保留适当精度（EPS 2 位小数、金额亿元 2 位小数、百分比 2 位小数）
- 每个核心结论必须有数据支撑
- 图表描述要具体（不说"呈上升趋势"，说"从 Q1 的 15.2% 升至 Q3 的 18.7%"）

## Phase 5: QC 验证

### 检查清单
- [ ] 公司名称和代码正确
- [ ] 财报期间正确（哪一年哪一季）
- [ ] 关键财务数字与 cn-stock-data 返回一致
- [ ] 同比/环比计算正确
- [ ] 没有使用训练数据中的旧数据
- [ ] 所有百分比数字加了 % 符号
- [ ] 金额单位统一（建议：亿元）
- [ ] 报告日期正确
