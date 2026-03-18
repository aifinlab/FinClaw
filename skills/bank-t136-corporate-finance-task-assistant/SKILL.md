---
name: bank-t136-corporate-finance-task-assistant
description: "当用户需要在银行对公场景下对企业偿债能力做快速诊断（短期到期压力、现金流覆盖、再融资可得性与备用偿债来源），并形成核验要点、补件清单、访谈问题与下一步动作建议时触发本技能。适合尽调/审查/贷后核查前的结构化快诊。"
---

# 企业偿债能力诊断助手

这个 skill 用来把“能不能还得上”拆成三层可核验问题：短期到期结构、现金流覆盖能力、备用偿债来源与触发条款。它不替代审批或风险处置决策，但会把需要补齐的证据链、最优先的核验动作、以及可落地的缓释条件写清楚。

输出目标是让使用者可以直接拿去做：

- 审查要点（阻断项/关注项/缓释条件）
- 贷后动作（到期管理、展期前核验、预警阈值与升级条件）
- 客户沟通提纲（“到期靠什么还/不续贷怎么办/资产能否处置”）

## 适用范围

- 授信审查：核验偿债闭环与再融资可得性，设置条件与预警阈值
- 贷后核查：出现“短债集中/展期诉求/欠息苗头”时快速定位压力来源
- 结构性分析：做“到期梯度表 + 现金流覆盖 + 备用来源”三件套

## 何时使用

- “未来12个月到期压力大，帮我看偿债能力到底靠什么”
- “经营现金流波动，能否覆盖利息与本金？”
- “想设置缓释条件：保证金、抵质押、回款监管、资金归集等”

## 何时不要使用

- 只有一句“负债高”没有任何债务结构、到期表、现金流数据时（应先输出缺口与补件）
- 用户要求虚构资产处置能力、融资承诺函或监管批复（明确拒绝）
- 需要审计/司法/估值结论才能确认的事项（本 skill 仅给核验路径）

## 默认工作流（建议按顺序输出）

1. **先做到期表**：未来 3/6/12 个月到期本金与利息，区分银行/非银/供应链金融/债券。
2. **再做覆盖测算**：经营现金流、可变现资产、已获授信未用额度、拟再融资。
3. **识别触发点**：交叉违约条款、担保代偿、重大诉讼、受限资金上升、关键客户流失。
4. **给出缓释条件**：资金监管、回款归集、补充担保、资产处置约束、债务重组计划。
5. **输出下一步动作**：补件、核验、访谈、监测指标与升级条件。

## 重点分析框架（写作骨架）

- **到期结构**：到期是否集中？能否滚续？哪些渠道是“硬到期”？
- **现金流覆盖**：`经营现金流` 能否覆盖利息？覆盖本金需要什么前提？
- **备用来源**：处置资产/股东支持/集团支持/新增融资的可得性与条件
- **触发条款**：交叉违约、担保代偿、监管受限、诉讼冻结
- **缓释与条件**：把风险点翻译成“可执行条件与监测阈值”

## 输入要求

最小可用输入见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\references\input-schema.md)。

## 输出要求

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：运行 `t136` 场景，生成“偿债能力诊断包”
- `..\shared\corporate_credit_skill_engine.py`：共享分析引擎（统一输出结构与规则）

## 参考资料与模板

- [solvency-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\references\solvency-checklist.md)
- [maturity-ladder-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\references\maturity-ladder-guide.md)
- [solvency-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\references\solvency-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\assets\example-input.json)
- [solvency-diagnosis-memo-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\assets\templates\solvency-diagnosis-memo-template.md)
- [maturity-ladder-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\assets\templates\maturity-ladder-template.md)
- [mitigation-conditions-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t136-corporate-finance-task-assistant\assets\templates\mitigation-conditions-template.md)

## 风险与边界

- 不把诊断建议写成审批结论；输出应明确依赖口径与证据链。
- 不虚构“股东兜底/政府支持/续贷承诺”；对支持性信息必须要求书面或可核验材料。
- 对“再融资可得性”只做条件化判断（前提是什么，缺什么证据）。

## 信息不足时的处理

- 即使缺数据，也要先输出“到期表缺口清单”和“最短补件路径”（到期表、授信批复、受限资金、现金流明细）。
- 对无法判断的部分，用“需要哪些字段/材料才能判断”表达，不空泛。

