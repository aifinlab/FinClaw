---
name: bank-t135-corporate-finance-task-assistant
description: "当用户需要在银行对公场景下对企业现金流压力做快速诊断、解释经营现金流恶化/断裂原因、形成补件与追问清单并给出下一步动作建议时触发本技能。适合尽调/审查/贷后核查前的结构化快诊与沟通提纲。"
---

# 企业现金流压力诊断助手

这个 skill 用于把“现金流紧张”从一句主观感受，拆成可核验的指标口径、可解释的驱动项、可补齐的证据链，以及可执行的下一步动作。它不直接输出“能不能贷/能不能批”的终结结论，而是帮助客户经理、审查人员、贷后人员快速回答三件事：

- 现金为什么变差（利润质量/周转占用/投资与筹资/表外与或有事项）
- 证据链缺什么（需要哪些报表、明细、合同、流水来把话说实）
- 下一步怎么做（访谈、核验、补件、监测与处置动作）

> 配套脚本基于共享引擎输出统一结构（摘要、缺口、红旗、核验要点、补件清单、问题清单、下一步动作），便于沉淀到日报/审查要点/贷后记录。

## 适用范围

- 授信尽调/审查：解释经营现金流与利润背离、识别占用与回款结构风险
- 贷后核查：出现“回款变慢、资金紧、展期诉求”时做快速定位与追问
- 客户经营：准备拜访/电话沟通前，把追问方向结构化

## 何时使用

- “经营现金流为负/明显下滑，帮我拆原因并列追问清单”
- “利润还不错但现金流差，怀疑应收/存货/预付占用”
- “短债压力大，现金头寸不够，想看压力源头和可行动作”

## 何时不要使用

- 用户要求基于极少信息直接给出确定性审批结论（应转为“信息缺口 + 核验路径”）
- 需要审计鉴证或司法结论才能确认的事项（本 skill 只能给核验要点与风险提示）
- 用户希望伪造/美化财务与流水材料（明确拒绝）

## 默认工作流（建议按顺序输出）

1. **先定口径**：现金流口径（合并/单体、是否含票据/保理、期间）、比较基线（同比/环比/预算）。
2. **做“利润-现金”快分解**：`经营现金流` vs `净利润`，先回答“差在非现金项目还是营运资本占用”。
3. **抓三条主线驱动项**：
   - **回款与占用**：应收、预付、存货、其他应收/关联占用、票据结构。
   - **资本性支出与对外支出**：CAPEX、股东分红/抽资、对外担保与代偿、对外投资。
   - **债务结构与到期**：短债滚续、到期集中度、现金流覆盖、备用资金来源。
4. **把判断落到证据链**：每条“可能原因”都要对应至少一个可核验材料/数据明细。
5. **输出下一步动作**：补件、访谈问题、核验要点、监测指标与升级条件。

## 重点分析框架（写作骨架）

- **现象确认**：现金流压力是“结构性”还是“短期波动”？是否存在口径变化造成的“假异常”？
- **驱动拆解**：利润质量（应计与现金）、营运资本占用（应收/存货/预付）、投资/筹资挤出。
- **压力传导**：回款变慢 -> 占用上升 -> 资金缺口 -> 借新还旧/票据腾挪 -> 风险暴露。
- **可行动作**：回款催收/折扣、压库存/收预付、调整账期、盘活存量资产、债务展期/置换条件。

## 输入要求

最小可用输入见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\references\input-schema.md)。

## 输出要求

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：运行 `t135` 场景，生成“现金流压力诊断包”
- `..\shared\corporate_credit_skill_engine.py`：共享分析引擎（统一输出结构与规则）

## 参考资料与模板

- [cashflow-pressure-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\references\cashflow-pressure-checklist.md)
- [cashflow-driver-tree.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\references\cashflow-driver-tree.md)
- [cashflow-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\references\cashflow-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\assets\example-input.json)
- [cashflow-diagnosis-memo-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\assets\templates\cashflow-diagnosis-memo-template.md)
- [driver-matrix-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\assets\templates\driver-matrix-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t135-corporate-finance-task-assistant\assets\templates\supplement-request-template.md)

## 风险与边界

- 不得把“诊断建议”写成“审批结论”；不得输出虚构的财务事实或外部查询结果。
- 对“可能原因”必须明确其证据依赖与可核验路径；无法核验时要标注为假设。
- 不把相关性当因果；对口径变化、季节性、一次性事件要单独提示。

## 信息不足时的处理

- 仍要输出：关键缺口清单 + 最短补件路径 + 优先核验顺序（先现金流口径，再回款占用，再到期压力）。
- 对缺少的指标，用“需要什么字段、为了验证什么假设、对应哪条风险”来表达，不要空泛要数。

