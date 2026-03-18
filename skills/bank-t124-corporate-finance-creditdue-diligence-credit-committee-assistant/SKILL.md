---
name: bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant
description: "当用户需要在银行对公金融场景下，为授信项目准备审批会材料、提炼支持与反对理由、识别核心争议点并形成待拍板事项时使用本技能。适合输出审批会一页纸、争议矩阵、有条件通过条款和会后推进动作。"
---

# 对公授信审批会要点生成助手

这个 skill 面向授信审批会场景使用。它不是最终批复工具，而是把客户经理、审查岗、风控、授信秘书等多方材料统一成“审批会可直接讨论和拍板”的结构化包。

它优先解决六类问题：

1. 这笔项目上会最该讨论的核心问题是什么
2. 支持与反对意见分别有哪些证据
3. 哪些争议点需要会上拍板，哪些可以会后补核验
4. 如拟“有条件通过”，条件应该怎么写才可执行
5. 当前是否具备上会条件，还是应暂缓上会
6. 会后推进动作和责任分工如何落地

## 适用范围

- 对公新增授信项目上会前材料整理
- 已审项目进入审批会前的争议点归并
- 续作、增额、展期项目的会前复核
- 需要输出一页纸、争议矩阵、待拍板事项时
- 需要将复杂尽调和审查结论转换为会议语言时

## 何时使用

- 用户说“帮我准备上会材料”“帮我做审批会摘要”“帮我列会上争议点”时
- 用户已拿到客户经理尽调和审查意见，但缺少会议版表达时
- 用户需要把问题分成支持理由、反对理由、待拍板事项时
- 用户需要形成可执行的“有条件通过条款”时

## 何时不要使用

- 用户要求直接输出最终批复文号、最终放款结论时
- 用户要求弱化重大风险、删改关键争议证据时
- 关键信息过于缺失，无法形成最小会议讨论闭环时
- 需要法律、审计、评估专项结论才可定性的事项，但用户要求本技能直接拍板时

## 默认工作流

1. 汇总项目基本盘：主体、金额、期限、用途、还款来源、增信方式。
2. 把材料按会议视角拆成支持理由、反对理由、争议点和待拍板事项。
3. 先识别阻断项，再识别可通过附加条件缓释的风险点。
4. 对每个争议点补上证据状态，区分“已确认”“待核验”“仅口径说明”。
5. 形成会议建议：暂缓上会、审慎上会、有条件上会、建议上会审议。
6. 输出会前材料包和会后推进动作，明确责任人和时序。

## 审批会核心分析框架

### 1. 是否具备上会前提

- 主体、用途、金额、还款来源是否明确
- 是否存在明显准入阻断项
- 核心材料是否达到可讨论水平

### 2. 支持与反对理由是否都站得住

- 支持理由有没有证据支撑
- 反对理由有没有被充分解释
- 双方依据是否建立在同一事实口径上

### 3. 争议点是否可拍板

- 哪些争议必须会上决策
- 哪些争议可附条件通过后继续核验
- 哪些事项必须会前补证据再上会

### 4. 有条件通过条款是否可执行

- 条款是否具体、可验证、可追责
- 是否有明确触发条件和时点
- 是否有会后跟踪动作和责任归口

## 输入要求

建议尽量提供：

- 企业主体信息：名称、行业、区域、实控人、治理结构
- 授信申请信息：品种、金额、期限、用途、提款安排、还款来源
- 财务和经营信息：收入、利润、现金流、应收、存货、订单和回款
- 存量授信和债务信息：他行借款、担保压力、逾期或续作情况
- 增信信息：保证、抵押、质押、回款控制措施
- 风险信息：涉诉处罚、舆情、担保链、关联交易等
- 会议目标：是否生成一页纸、争议矩阵、待拍板事项、条件通过条款

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\references\input-schema.md)。

## 输出要求

默认输出至少包含：

1. 项目概况与会议阶段
2. 上会阻断项
3. 支持理由与反对理由
4. 核心争议点与待拍板事项
5. 证据缺口和会前补件要求
6. 有条件通过条款建议
7. 初步会议建议与会后动作
8. 会议版一页纸摘要

## 配套脚本

- `scripts/corporate_credit_committee_packet.py`：生成审批会材料包
- `scripts/run_skill.py`：脚本入口

示例调用：

```bash
python scripts/run_skill.py --input assets/example-input.json --output committee_packet.md --format markdown
```

## 参考资料与模板

- [credit-committee-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\references\credit-committee-checklist.md)
- [debate-matrix-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\references\debate-matrix-guide.md)
- [key-vote-issues.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\references\key-vote-issues.md)
- [conditional-approval-framework.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\references\conditional-approval-framework.md)
- [committee-one-page-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\assets\templates\committee-one-page-template.md)
- [debate-matrix-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\assets\templates\debate-matrix-template.md)
- [conditional-approval-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant\assets\templates\conditional-approval-template.md)

## 风险与边界

- 本技能输出的是会议准备材料和初步会议建议，不是最终审批批复。
- 对未核验事项必须明确标注，不能写成既定事实。
- 不得因“推动通过”而有意删减反对理由或风险证据。
- 有条件通过条款必须可执行，避免口号式条件。
- 需要专项意见的事项应明确建议升级至法务、评估、审计等岗位。

## 信息不足时的处理

- 如果资料不全，先输出争议点、补件要求和暂缓上会建议。
- 如果支持和反对证据都不足，优先提示“暂不具备拍板条件”。
- 如果阻断项已出现，先给阻断项清单和解除条件，再谈上会建议。

## 交付标准

- 参会人员能快速看懂支持与反对逻辑，不需要二次翻译。
- 每个争议点都对应证据状态和建议动作。
- 有条件通过条款可执行、可跟踪、可验收。
- 输出能直接用于会前沟通和会后跟踪。
