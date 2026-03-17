---
name: banking-workflow-orchestrator
description: 银行业务流程编排器，将多个银行数据分析Skills按业务链路串联执行。当用户提出跨多个分析环节的复合业务需求时（如"帮我做一次完整的AML排查"、"做一套客户经营分析"、"全面分析存贷款经营情况"），自动识别所需的Skill链路、确定执行顺序、在节点间传递数据，并在关键节点请求用户确认。
---

# 银行业务流程编排器

## 1. 业务问题

银行数据分析体系包含25个专项分析Skills，分布在经营分析、客户经营、渠道交易、风险合规四大领域。单个Skill解决单点问题，但实际业务场景往往需要多个Skill协同——例如一次完整的反洗钱排查需要依次完成初筛、异常识别、聚类分析；一次客户经营闭环需要从客户画像出发，经过分层、预警、渗透分析，最终输出机会清单。

当前痛点：用户需要自己记住Skill之间的依赖关系和数据传递逻辑，手动逐个调用并搬运中间结果。本编排器解决这个问题——用户只需描述业务目标，编排器自动规划执行链路、按序调用、传递数据、输出最终结果。

## 2. 适用场景

- 用户提出需要多个Skill协作的复合分析需求
- 用户明确要求"完整流程"、"全链路分析"、"端到端排查"
- 用户描述的业务目标横跨多个分析环节（如"从客户画像到机会清单"）
- 用户不确定该用哪些Skill，描述了业务场景希望系统自动匹配
- 季末/年末需要批量执行多条业务分析链路

## 3. 输入

| 输入项 | 说明 | 是否必须 |
|--------|------|----------|
| 业务目标描述 | 用户用自然语言描述的分析需求 | 必须 |
| 原始数据/文件 | 链路起点Skill所需的输入数据 | 必须 |
| 链路选择 | 指定执行哪条预定义链路（可选，不指定则自动识别） | 可选 |
| 执行模式 | 全自动 / 逐步确认（默认逐步确认） | 可选 |
| 中间结果调整 | 用户对某个节点输出的修正或补充 | 可选 |

## 4. 输出

- **链路规划报告**：识别出的执行链路、包含的Skill节点、预计步骤数
- **各节点输出**：每个Skill节点的独立分析结果（保持原Skill的输出格式）
- **节点间数据映射**：上游输出如何映射为下游输入的说明
- **最终汇总结果**：链路终端Skill的输出，即业务流程的最终交付物
- **执行日志**：链路执行过程摘要（哪些节点已完成、耗时、数据量）

## 5. 预定义业务链路

以下是从25个Skills的依赖关系中提取的标准业务链路。

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

- **触发词**：资金流向、大额资金追踪、账户异动、资金链路分析
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

## 6. 执行框架

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
2. **调用Skill**：按该Skill的SKILL.md定义执行分析
3. **输出暂存**：保存本节点输出，供下游节点使用
4. **检查点**（逐步确认模式下）：向用户展示本节点结果摘要，询问是否继续

对于可并行的节点（如客户链路中的4个分析节点），同时启动执行以提高效率。

### 第四步：数据映射与传递

节点间数据传递遵循以下规则：

- **字段映射**：上游输出中与下游输入同名的字段直接传递
- **结构转换**：如果上下游数据结构不同，编排器负责转换（如从"客户分层结果"提取"高价值客户列表"作为流失预警的输入范围）
- **数据过滤**：下游只需要上游输出的子集时，编排器负责筛选
- **缺失处理**：如果上游未产出下游必需的字段，暂停并提示用户

### 第五步：汇总与交付

链路执行完毕后：

1. 输出终端Skill的最终结果
2. 附上执行日志摘要（各节点完成状态、关键数据量）
3. 如果有节点未能正常完成，说明原因和影响范围

## 7. 安全边界

- 不编造数据；不夸大结论；缺失信息标注"未获取"或"待核实"
- 不替代正式审批、正式风控、正式合规、正式报送、正式处置、正式责任认定、正式管理决策
- 编排器本身不进行业务分析，仅负责链路调度和数据传递；分析逻辑完全由各Skill自身承担
- 各Skill的安全边界在链路执行中同样生效，编排器不会绕过任何单个Skill的安全限制
- 风险合规链路的输出仅供数据分析和复核参考，不替代正式合规判定、可疑交易报告（STR）、审计调查或账户处置决策
- 客户经营链路的输出仅作为经营参考，不替代营销准入判断、授信审批决策、客户适当性评估
- 逐步确认模式下，每个关键节点的输出需用户确认后才继续，防止错误数据在链路中传播

## 8. 上游依赖

本Skill依赖所有25个银行数据分析Skills，按需调用：

| 领域 | 可调用Skills |
|------|-------------|
| 经营分析 | business-metrics-attribution, business-analysis-summary, branch-performance-benchmarking, deposit-growth-attribution, loan-structure-analysis, bank-calc-utils |
| 客户经营 | bank-customer-360, customer-segmentation, customer-churn-alert, customer-product-penetration, customer-opportunity-list-generation, dormant-account-analysis, early-repayment-churn-analysis, segment-credit-performance |
| 渠道交易 | channel-transaction-performance, payment-failure-attribution, fund-flow-analysis, large-fund-movement-tracking, account-volatility-monitoring |
| 风险合规 | suspicious-transaction-screening, transaction-flow-anomaly-detection, high-risk-transaction-clustering, risk-customer-behavior-change, watchlist-match-result-analysis, regulatory-reporting-quality-validation |

## 9. 可联动下游 Skills

无（顶层编排Skill，输出直接面向用户）
