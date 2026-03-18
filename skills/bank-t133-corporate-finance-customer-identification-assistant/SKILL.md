---
name: bank-t133-corporate-finance-customer-identification-assistant
description: "当用户需要在银行对公金融场景下，围绕客户识别进行持续监测、风险扫描、异常识别或预警提示时使用本技能。适合输出风险信号摘要、优先级判断、处置建议和升级路径。"
---

# 上下游客户识别助手

这个 skill 面向上下游客户识别场景，重点不是直接做授信结论，而是帮助用户从交易样本、发票流水、名单和链路关系中识别关键上游、关键下游和重点排查对象。它适合用于拓客线索挖掘、链路排查和重点客户分层。

## 适用范围
- 基于交易、合同、票据、回款样本识别上下游客户
- 围绕核心企业或目标客户挖掘上下游名单
- 客户经理、审查支持和业务中台的链路识别场景
- 需要输出优先名单、识别规则、排查建议和跟进动作时

## 何时使用
- 用户说“帮我识别这家企业的上下游客户”“从样本里找重点上下游”时
- 用户已有交易样本、发票、客户名单，希望形成结构化识别结果时
- 用户需要把识别结果转成拓客优先级或排查优先级时

## 何时不要使用
- 用户要求凭单个样本直接认定客户关系或业务真实性时
- 没有识别目标、没有样本、没有时间窗口时
- 用户要求把识别工具直接当成最终风控结论时

## 默认工作流
1. 明确识别目标，是上游、下游、关键客户还是重点排查名单。
2. 确定时间窗口、样本范围和识别口径。
3. 根据交易频次、金额、稳定性和链路关系做初步识别和分层。
4. 区分高价值目标、一般目标和待核验目标。
5. 输出优先名单、排查路径和后续动作。

## 重点分析框架
- 样本质量：时间窗口、覆盖率和样本偏差
- 客户识别：交易频次、金额占比、持续稳定性
- 关系判断：真实外部客户、关联方还是一次性交易对手
- 优先级输出：拓客优先、排查优先或持续观察

## 输入要求
- 核心主体和识别目标说明
- 交易样本、发票、流水、客户名单和样本窗口
- 交易金额、频次、回款和链路关系信息
- 需要输出的名单类型，如重点拓客、重点排查或重点观察

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\references\input-schema.md)。

## 输出要求
- 客户识别摘要与初步建议
- 高优先级上下游客户名单思路
- 资料缺口、识别偏差和补充样本要求
- 排查路径、跟进建议和升级条件

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出上下游客户识别包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含客户识别专项规则

## 参考资料与模板

- [customer-identification-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\references\customer-identification-checklist.md)
- [sampling-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\references\sampling-guide.md)
- [identification-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\references\identification-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\assets\example-input.json)
- [customer-list-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\assets\templates\customer-list-template.md)
- [identification-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\assets\templates\identification-note-template.md)
- [follow-up-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t133-corporate-finance-customer-identification-assistant\assets\templates\follow-up-template.md)

## 风险与边界
- 不得把识别结果直接写成确定性客户关系或授信结论。
- 不得编造样本、名单或交易关系。
- 对样本不足或识别偏差较大的结果，必须明确标注边界。
- 涉及关联方、名单筛查或合规判断时，应转入相应专项流程。

## 信息不足时的处理
- 如果样本不足，先输出识别框架、补样本要求和初步名单方向。
- 如果目标不清楚，先要求明确是拓客、排查还是链路画像。
- 对无法确认的客户关系，标注为待核验，不写成已确认客户。

## 交付标准
- 输出能直接支持客户经理或中台做上下游识别和跟进。
- 识别结论要说清楚依据、样本范围和不确定性。
- 至少回答“识别到了谁、为什么是他们、下一步怎么跟进”三个问题。
