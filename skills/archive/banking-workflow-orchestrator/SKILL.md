---
name: banking-workflow-orchestrator
description: |
  银行业务数据分析统一入口。覆盖经营分析、客户经营、渠道交易、风险合规四大领域共25项专项分析能力。
  经营分析：银行经营指标归因（存款/贷款/利润/净息差变动拆解）、支行网点排名对标、存款增减归因（新增/流失/迁移）、贷款结构分析、经营分析会摘要汇报、银行指标计算（同比/环比/贡献度/拨备覆盖率）。
  客户经营：银行客户360画像、客户分层分群、流失预警、产品渗透交叉销售、经营机会清单、休眠账户激活、提前还款挽留、客群授信表现。
  渠道交易：银行渠道交易表现、支付失败归因、银行资金流向分析、大额资金追踪、账户波动监测。
  风险合规：可疑交易筛查、交易异常模式识别、高风险交易聚类、风险客户行为监测、名单匹配分析、监管报送质量校验。
  支持单项银行分析和多技能链路编排（反洗钱全链路、客户经营闭环、经营分析汇报等）。
---

# 银行业务数据分析统一入口

## 1. 路由表

收到用户的银行业务分析请求后，按以下路由表匹配目标子 skill。

路径前缀：`/Users/chengdongpo/Documents/AIProjects/finclaw-workspace/finclaw/skills/`

| 领域 | 触发关键词 | 目标 sub-skill | SKILL.md 路径 |
|------|-----------|---------------|--------------|
| 经营分析 | 存款下降原因、贷款增长驱动、利润变动归因、净息差变动拆解、中间业务收入波动、不良率变动成因、经营指标归因 | business-metrics-attribution | `business-metrics-attribution/SKILL.md` |
| 经营分析 | 支行排名、分行对比、网点对标、机构绩效差距、支行存款规模对比 | branch-performance-benchmarking | `branch-performance-benchmarking/SKILL.md` |
| 经营分析 | 存款增长来源、存款流失分析、新增客户存款、定期续存率、活期转定期、存款冲量回落 | deposit-growth-attribution | `deposit-growth-attribution/SKILL.md` |
| 经营分析 | 贷款结构、贷款余额分布、贷款集中度、信贷结构分析 | loan-structure-analysis | `loan-structure-analysis/SKILL.md` |
| 经营分析 | 经营分析会、行长办公会、管理层汇报、经营情况总结、经营分析摘要 | business-analysis-summary | `business-analysis-summary/SKILL.md` |
| 经营分析 | 同比增速计算、环比变动率、贡献度占比、不良率计算、拨备覆盖率、净息差计算、银行指标计算 | bank-calc-utils | `bank-calc-utils/SKILL.md` |
| 客户经营 | 客户画像、客户360、客户全景、客户基本信息 | bank-customer-360 | `bank-customer-360/SKILL.md` |
| 客户经营 | 客户分层、客户分群、客户价值分级、差异化经营 | customer-segmentation | `customer-segmentation/SKILL.md` |
| 客户经营 | 客户流失预警、流失风险、客户降级、资产下降预警 | customer-churn-alert | `customer-churn-alert/SKILL.md` |
| 客户经营 | 产品渗透率、交叉销售、产品持有率、单产品依赖 | customer-product-penetration | `customer-product-penetration/SKILL.md` |
| 客户经营 | 机会清单、经营机会、客户经理任务、营销清单 | customer-opportunity-list-generation | `customer-opportunity-list-generation/SKILL.md` |
| 客户经营 | 休眠账户、沉睡资金、账户激活、唤醒 | dormant-account-analysis | `dormant-account-analysis/SKILL.md` |
| 客户经营 | 提前还款、提前结清、还款挽留、提前还贷 | early-repayment-churn-analysis | `early-repayment-churn-analysis/SKILL.md` |
| 客户经营 | 客群授信表现、授信审批通过率、客群信贷质量、分群授信 | segment-credit-performance | `segment-credit-performance/SKILL.md` |
| 渠道交易 | 渠道交易量、渠道成功率、渠道表现、渠道经营 | channel-transaction-performance | `channel-transaction-performance/SKILL.md` |
| 渠道交易 | 支付失败、支付错误码、交易失败归因、支付成功率下降 | payment-failure-attribution | `payment-failure-attribution/SKILL.md` |
| 渠道交易 | 银行资金流向、资金来源去向、资金迁移路径、资金结构 | fund-flow-analysis | `fund-flow-analysis/SKILL.md` |
| 渠道交易 | 大额资金、大额转账追踪、资金集中进出、短停转出 | large-fund-movement-tracking | `large-fund-movement-tracking/SKILL.md` |
| 渠道交易 | 账户余额波动、账户异动、AUM剧烈变化、异常活跃账户 | account-volatility-monitoring | `account-volatility-monitoring/SKILL.md` |
| 风险合规 | 可疑交易筛查、交易监测初筛、合规筛查、STR筛查 | suspicious-transaction-screening | `suspicious-transaction-screening/SKILL.md` |
| 风险合规 | 交易异常模式、交易流水异常、异常账户识别 | transaction-flow-anomaly-detection | `transaction-flow-anomaly-detection/SKILL.md` |
| 风险合规 | 高风险交易聚类、交易模式聚类、跨簇关联 | high-risk-transaction-clustering | `high-risk-transaction-clustering/SKILL.md` |
| 风险合规 | 风险客户行为变化、高风险客户监测、客户行为趋势 | risk-customer-behavior-change | `risk-customer-behavior-change/SKILL.md` |
| 风险合规 | 名单匹配、名单筛查复核、制裁名单、黑名单匹配 | watchlist-match-result-analysis | `watchlist-match-result-analysis/SKILL.md` |
| 风险合规 | 监管报送校验、报送数据质量、报送完整性、监管报表校验 | regulatory-reporting-quality-validation | `regulatory-reporting-quality-validation/SKILL.md` |

## 2. 分发逻辑

收到用户请求后：

1. **判断单技能 vs 多技能**
   - 多技能信号：用户要求"完整流程/全链路/端到端"，或意图横跨 2+ 路由条目
   - 单技能信号：意图匹配路由表中单一条目（默认模式）

2. **单技能分发**：
   - 匹配路由表 → Read 对应 SKILL.md → 按其分析框架执行
   - bank-calc-utils 作为计算基础设施随时可用

3. **多技能链路分发**：
   - 匹配预定义链路（见第4节）或组装自定义链路 → 进入链路编排模式

4. **歧义处理**：
   - 若匹配多个子 skill，列出候选询问用户
   - 若无法匹配任何路由条目，告知用户当前能力范围

## 3. 单技能分发协议

当确定为单技能查询时：

1. 从路由表找到目标 sub-skill
2. 使用 Read 工具读取该 skill 的 SKILL.md（路径前缀 + 表中路径）
3. 完全按照该 SKILL.md 的分析框架执行（输入要求、分析步骤、输出格式）
4. 输出末尾注明使用了哪个分析模块，例如：`> 本次分析使用：deposit-growth-attribution（存款增减归因分析）`

## 4. 预定义业务链路

以下是从25个Skills的依赖关系中提取的标准业务链路，适用于多技能编排场景。

### 链路一：反洗钱全链路排查（AML Pipeline）

```
suspicious-transaction-screening  →  transaction-flow-anomaly-detection  →  high-risk-transaction-clustering
       初筛命中交易                        异常模式识别                          聚类分析输出复核清单
```

- **触发词**：反洗钱、AML、可疑交易排查、交易监测全流程
- **起点输入**：交易流水数据、筛查规则（或使用默认规则）
- **终点输出**：按模式聚类的高风险交易清单，附复核优先级
- **数据传递**：初筛命中交易集 → 异常识别的输入交易集 → 聚类分析的候选集

### 链路二：客户经营闭环（Customer Operations Loop）

```
bank-customer-360  →  customer-segmentation  →  ┬─ customer-churn-alert
                                                 ├─ customer-product-penetration
                                                 ├─ dormant-account-analysis
                                                 └─ early-repayment-churn-analysis
                                                          ↓ （全部汇入）
                                                 customer-opportunity-list-generation
```

- **触发词**：客户经营分析、客户全景、机会清单、客户经理任务
- **起点输入**：客户基础数据（账户、交易、持仓、行为）
- **终点输出**：按优先级排序的客户经营机会清单
- **数据传递**：客户360画像 → 分层结果 → 分发给4个并行分析节点 → 结果汇入机会清单生成
- **并行节点**：churn-alert、product-penetration、dormant-analysis、early-repayment可并行执行，互不依赖

### 链路三：经营分析汇报（Business Analysis Report）

```
┬─ business-metrics-attribution
├─ branch-performance-benchmarking
├─ deposit-growth-attribution      →  business-analysis-summary
├─ loan-structure-analysis
└─ bank-calc-utils（计算支撑）
```

- **触发词**：经营分析报告、管理层汇报、经营情况总结、季度经营回顾
- **起点输入**：经营指标数据（存款、贷款、收入、网点数据等）
- **终点输出**：面向管理层的经营分析摘要
- **数据传递**：各专项分析结果 → 汇入摘要生成；bank-calc-utils在各节点按需调用
- **并行节点**：metrics-attribution、branch-benchmarking、deposit-attribution、loan-structure可并行执行
- **灵活性**：用户可选择只执行部分专项（如只做存款归因+贷款结构），摘要生成适配实际提供的输入

### 链路四：资金异动监测（Fund Movement Monitoring）

```
fund-flow-analysis  →  large-fund-movement-tracking  ↔  account-volatility-monitoring
   资金流向分析              大额资金追踪                    账户波动监测
```

- **触发词**：银行资金流向全链路、大额资金追踪、账户异动全面排查、资金链路分析
- **起点输入**：账户交易流水、资金变动记录
- **终点输出**：大额资金链路图 + 异常波动账户清单
- **数据传递**：资金流向分析结果 → 大额追踪的关注账户范围；大额追踪发现的异常账户 ↔ 波动监测的监控对象
- **双向关联**：large-fund-movement-tracking与account-volatility-monitoring互为参考

### 链路五：渠道支付诊断（Channel Payment Diagnosis）

```
payment-failure-attribution  →  channel-transaction-performance
     支付失败归因                   渠道交易表现分析
```

- **触发词**：支付失败分析、渠道表现、交易成功率下降、支付诊断
- **起点输入**：支付交易明细（含失败记录）
- **终点输出**：渠道维度的交易表现报告，含失败归因和改进建议

### 自定义链路

用户可以指定任意Skill组合构建自定义链路，编排器负责：
1. 校验依赖关系是否合理（上游Skill的输出能否对接下游Skill的输入）
2. 如果存在缺失的中间节点，提示用户补充
3. 按依赖拓扑排序确定执行顺序

## 5. 执行框架（多技能链路模式）

### 第一步：意图识别与链路匹配

收到用户请求后：

1. 从业务描述中提取关键意图（分析什么、分析谁、什么目的）
2. 匹配预定义链路，或根据意图组装自定义链路
3. 输出链路规划：包含哪些节点、执行顺序、预计步骤数
4. **请求用户确认链路规划**，再开始执行

### 第二步：数据就绪检查

执行前检查起点Skill所需的输入数据：

- 数据是否已提供
- 数据格式是否符合要求
- 如有缺失，明确告知用户需要补充什么

### 第三步：逐节点执行

按拓扑顺序执行链路中的每个Skill节点：

1. **准备输入**：从上游节点输出中提取本节点所需的输入字段
2. **调用Skill**：Read 对应 SKILL.md → 按该Skill定义执行分析
3. **输出暂存**：保存本节点输出，供下游节点使用
4. **检查点**（逐步确认模式下）：向用户展示本节点结果摘要，询问是否继续

对于可并行的节点（如客户链路中的4个分析节点），同时启动执行以提高效率。

### 第四步：数据映射与传递

节点间数据传递遵循以下规则：

- **字段映射**：上游输出中与下游输入同名的字段直接传递
- **结构转换**：如果上下游数据结构不同，编排器负责转换
- **数据过滤**：下游只需要上游输出的子集时，编排器负责筛选
- **缺失处理**：如果上游未产出下游必需的字段，暂停并提示用户

### 第五步：汇总与交付

链路执行完毕后：

1. 输出终端Skill的最终结果
2. 附上执行日志摘要（各节点完成状态、关键数据量）
3. 如果有节点未能正常完成，说明原因和影响范围

## 6. 安全边界

- 不编造数据；不夸大结论；缺失信息标注"未获取"或"待核实"
- 不替代正式审批、正式风控、正式合规、正式报送、正式处置、正式责任认定、正式管理决策
- 单技能模式下完全遵循子 skill 的安全边界
- 链路模式下各Skill的安全边界同样生效，编排器不会绕过任何单个Skill的安全限制
- 风险合规链路的输出仅供数据分析和复核参考，不替代正式合规判定、可疑交易报告（STR）、审计调查或账户处置决策
- 客户经营链路的输出仅作为经营参考，不替代营销准入判断、授信审批决策、客户适当性评估
- 逐步确认模式下，每个关键节点的输出需用户确认后才继续，防止错误数据在链路中传播

## 7. 上游依赖

本Skill依赖所有25个银行数据分析Skills，按需调用：

| 领域 | 可调用Skills |
|------|-------------|
| 经营分析 | business-metrics-attribution, business-analysis-summary, branch-performance-benchmarking, deposit-growth-attribution, loan-structure-analysis, bank-calc-utils |
| 客户经营 | bank-customer-360, customer-segmentation, customer-churn-alert, customer-product-penetration, customer-opportunity-list-generation, dormant-account-analysis, early-repayment-churn-analysis, segment-credit-performance |
| 渠道交易 | channel-transaction-performance, payment-failure-attribution, fund-flow-analysis, large-fund-movement-tracking, account-volatility-monitoring |
| 风险合规 | suspicious-transaction-screening, transaction-flow-anomaly-detection, high-risk-transaction-clustering, risk-customer-behavior-change, watchlist-match-result-analysis, regulatory-reporting-quality-validation |
