---
name: bank-t139-corporate-finance-task-assistant
description: "当用户需要在银行对公场景下对企业舆情异常做预警分级、识别高风险信号、形成核验要点与跟进处置动作，并输出可用于日报/周报/事件通报的结构化内容时触发本技能。适合贷后监测、授信存量管理与风险事件初筛。"
---

# 企业舆情异常预警助手

舆情预警的目标不是“汇总新闻”，而是把分散信号转成可执行动作：先分级（严重度/可信度/扩散性），再核验（证据链与硬事件），最后给出处置（跟进动作、升级条件、沟通口径）。

这个 skill 会输出统一结构的“预警包”：摘要、信息缺口、红旗、核验要点、补件清单、沟通问题、下一步动作，便于直接落地到贷后监测、存量授信管理、风险事件通报。

## 适用范围

- 贷后监测：负面舆情、司法风险、监管处罚、重大事故、经营异常的初筛与升级
- 存量授信管理：把舆情信号翻译成“需要核验什么、要不要升级、怎么处置”
- 客户经营：准备沟通前先做“事件分诊 + 追问清单 + 口径建议”

## 何时使用

- “最近这家企业负面新闻多，帮我判断严重程度与跟进动作”
- “想把舆情信号写进贷后日报/周报/事件通报”
- “需要预警分级规则与升级条件（什么时候要风控/法务介入）”

## 何时不要使用

- 用户要求仅凭传言做违法违规定性或处罚结论（应转为核验要点与证据链）
- 需要监管/司法正式结论才能确认的事项（本 skill 只能做初筛与动作建议）
- 用户要求伪造外部新闻、监管处罚或司法裁判文书（明确拒绝）

## 默认工作流（建议按顺序输出）

1. **定口径**：时间窗口、信息来源范围（用户提供/公开披露/第三方监测），以及“只做初筛不做定性”的边界。
2. **信号归类**：司法/监管/安全生产/欠薪/停工/重大客户流失/债务风险/经营异常。
3. **分级**（至少三维）：
   - 严重度：是否触及停产、重大诉讼冻结、监管处罚、兑付风险等硬事件
   - 可信度：是否有权威来源、是否可交叉验证、是否存在谣言可能
   - 扩散性：是否持续、多平台发酵、是否影响上下游与金融机构
4. **映射影响**：对现金流、融资渠道、授信条款触发、押品价值/处置的潜在影响（条件化表达）。
5. **给出动作**：优先核验事项、客户沟通提纲、监测指标与升级条件（风控/法务/合规）。

## 重点分析框架（写作骨架）

- 事件是什么（事实摘要 + 时间线）
- 是否硬事件（司法冻结/监管处罚/重大事故/兑付违约等）
- 影响路径（经营 -> 现金流 -> 融资 -> 授信条款/押品 -> 风险暴露）
- 缺口与核验（最短证据链）
- 动作与升级（谁负责、什么时候升级、升级后做什么）

## 输入要求

最小可用输入见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\references\input-schema.md)。

## 输出要求

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：运行 `t139` 场景，生成“舆情异常预警包”
- `..\shared\corporate_credit_skill_engine.py`：共享引擎（统一输出结构与规则）

## 参考资料与模板

- [public-opinion-triage-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\references\public-opinion-triage-guide.md)
- [public-opinion-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\references\public-opinion-red-flags.md)
- [escalation-playbook.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\references\escalation-playbook.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\assets\example-input.json)
- [public-opinion-warning-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\assets\templates\public-opinion-warning-note-template.md)
- [event-triage-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\assets\templates\event-triage-template.md)
- [followup-action-plan-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t139-corporate-finance-task-assistant\assets\templates\followup-action-plan-template.md)

## 风险与边界

- 不把舆情信号当作事实定性；必须区分“已确认事实/待核验信息/推测影响”。
- 不输出诽谤式内容；对负面信息要标注时间窗口与来源摘要（若用户提供）。
- 不替代风控/法务/合规的正式事件认定与处置决定。

## 信息不足时的处理

- 如果只有“负面新闻数量”没有事件摘要：先输出“需要哪些信息才能分级”的补件清单与核验路径。
- 如果事件高度不确定：优先输出“低成本核验动作 + 监测指标 + 升级条件”，避免过度反应或漏报。

