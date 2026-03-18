---
name: bank-t132-corporate-finance-due-diligence-supply-chain-assistant
description: "当用户需要在银行对公金融场景下，围绕供应链尽调进行初筛、尽调、准入或审批前梳理时使用本技能。适合输出面向对公客户经理、审查人员和业务中台的结构化判断、待补资料清单、关键风险提示和下一步推进建议。"
---

# 供应链核心企业尽调助手

这个 skill 面向供应链尽调场景，重点不是只看申请主体，而是把核心企业、链路角色、真实贸易、应收回款和物流单据放到同一条链路里判断。它适合处理“这笔供应链融资到底是不是围绕真实链路发生”的问题。

## 适用范围

- 围绕核心企业上下游的供应链融资尽调
- 订单、合同、物流、发票、回款和应收账款核验
- 客户经理尽调、审查支持和供应链业务中台复核
- 需要输出供应链闭环真实性判断、补件要求和下一步动作时

## 何时使用

- 用户说“帮我看这条供应链能不能做”“先核验核心企业和贸易背景”时
- 用户已有核心企业、上下游合同、物流和应收资料，希望做结构化判断时
- 用户需要把供应链融资结论拆成链路真实性、核心企业信用和应收可验证性三层时

## 何时不要使用

- 用户要求直接输出最终批复或放款结论时
- 用户要求伪造贸易背景、包装应收账款或弱化链路风险时
- 缺少核心企业、贸易链路和应收验证材料时

## 默认工作流
1. 明确申请主体、核心企业、供应链角色和融资模式。
2. 核验订单、合同、发票、物流、验收和回款能否串成真实贸易闭环。
3. 判断核心企业信用、链路稳定性和应收账款可验证性。
4. 拆分硬性阻断项、重点核验项和可补证据后推进事项。
5. 输出供应链尽调结论、补件清单和后续推进建议。

## 重点分析框架
- 核心企业信用：付款能力、付款习惯、确权和合作稳定性
- 链路真实性：合同、物流、发票、验收、回款是否闭环
- 应收验证：账龄、确权、回款路径和重复融资风险
- 链路稳定性：单一核心企业依赖度、上下游集中度和履约争议
- 融资适配性：融资结构是否真正嵌入供应链场景

## 输入要求
- 申请主体、核心企业和上下游角色信息
- 授信金额、用途、期限、还款来源和融资模式
- 订单、合同、发票、物流、验收、回款等贸易链材料
- 应收账款账龄、确权情况、回款账户和历史合作情况
- 财务摘要、外部风险、授信存量和担保情况

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\references\input-schema.md)。

## 输出要求
- 供应链尽调摘要与初步建议
- 供应链闭环真实性判断
- 核心企业和链路稳定性判断
- 资料缺口、补件要求和核验重点
- 风险提示和后续推进动作

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出供应链尽调判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含供应链专项规则

## 参考资料与模板

- [supply-chain-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\references\supply-chain-checklist.md)
- [trade-chain-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\references\trade-chain-guide.md)
- [supply-chain-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\references\supply-chain-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\assets\example-input.json)
- [supply-chain-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\assets\templates\supply-chain-note-template.md)
- [receivable-check-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\assets\templates\receivable-check-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t132-corporate-finance-due-diligence-supply-chain-assistant\assets\templates\supplement-request-template.md)

## 风险与边界
- 不得把初步判断包装成最终授信批复或放款结论。
- 不得编造贸易背景、物流、应收或核心企业支持事实。
- 未经核验的口头确权、口头付款安排和口头合作关系，必须标为待核验。
- 资料严重缺失时必须降级表达，不得硬给“可做”结论。

## 信息不足时的处理
- 先输出已知链路事实，再列缺失的核心企业、合同、物流和应收证据。
- 如果闭环证据不足，优先生成补件清单和重点核验动作。
- 对无法确认的贸易背景和应收状态，不得写成既成事实。

## 交付标准
- 输出应让客户经理、审查岗和业务中台快速看懂供应链链路是否成立。
- 关键判断要落到核心企业、贸易链、应收验证和回款路径上。
- 至少回答“链路是不是真、核心企业稳不稳、钱怎么回来”三个问题。
