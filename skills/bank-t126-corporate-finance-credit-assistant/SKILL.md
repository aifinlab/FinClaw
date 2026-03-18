---
name: bank-t126-corporate-finance-credit-assistant
description: "当用户需要在银行对公金融场景下，对小微企业授信做经营真实性判断、税票流水核验、普惠准入排查、补件清单整理和初步推进建议输出时使用本技能。适合服务客户经理、普惠审批支持和业务中台。"
---

# 小微企业授信助手

这个 skill 聚焦小微企业和普惠授信场景，不强调复杂集团结构，而是重点判断企业是否真实经营、税票流水能否印证收入、融资需求是否符合周转逻辑，以及授信金额是否匹配经营体量。它的核心价值是把“看起来像能做”进一步拆成“为什么能做、还缺什么、哪里要谨慎”。

## 适用范围

- 小微企业流贷、经营贷、普惠授信的前端判断
- 客户经理报送前自检、业务中台预审
- 经营真实性、税票流水匹配、法人稳定性核验
- 需要输出普惠准入判断、补件清单和下一步建议时
- 需要为现场走访、电话访谈或普惠预审准备问题清单时

## 何时使用

- 用户说“帮我看这家小微能不能做”“先做一轮普惠准入排查”时
- 已有基础工商、流水、纳税、合同或发票材料，希望做结构化判断时
- 需要快速判断“小微客户现在是可推进、补件推进还是应升级审查”时

## 何时不要使用

- 用户要求直接给出最终审批结论、批复条件或放款结论时
- 用户要求包装流水、拼接交易或伪造经营材料时
- 缺少最基本的企业名称、申请金额、用途和还款来源时

## 默认工作流

1. 确认主体、申请金额、用途、期限和还款来源。
2. 核验税票、流水、订单、场地和上下游信息是否能形成经营闭环。
3. 识别经营真实性、法人稳定性、授信依赖度和外部负面风险。
4. 输出准入建议、补件要求、沟通问题和后续核查动作。
5. 如命中明显红旗，转为审慎推进或升级审查，不直接给乐观结论。

## 重点分析框架

- 主体真实性：工商、场地、人员、行业和实际经营是否一致
- 经营闭环：订单、发票、纳税、流水、回款是否互相印证
- 还款逻辑：资金用途和第一还款来源是否可验证
- 风险暴露：法人负面、对外担保、涉诉、交叉融资、税票异常
- 普惠适配：额度、期限、用款节奏是否与小微经营节奏匹配

## 输入要求

- 企业主体、实控人、成立年限、主营业务
- 授信申请金额、用途、期限、还款来源
- 纳税申报、流水、合同、发票、经营场地或库存信息
- 存量授信、外部负面、担保方式、客户与供应商情况

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\references\input-schema.md)。

## 输出要求

- 小微授信摘要与初步建议
- 经营真实性和税票流水匹配判断
- 资料缺口与补件清单
- 风险信号、沟通问题和现场核验重点
- 后续推进或升级审查建议

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出小微企业授信判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含小微场景专项规则

## 参考资料与模板

- [sme-admission-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\references\sme-admission-checklist.md)
- [tax-invoice-bankflow-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\references\tax-invoice-bankflow-guide.md)
- [sme-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\references\sme-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\assets\example-input.json)
- [sme-credit-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\assets\templates\sme-credit-note-template.md)
- [field-visit-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\assets\templates\field-visit-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t126-corporate-finance-credit-assistant\assets\templates\supplement-request-template.md)

## 风险与边界

- 本技能不能替代正式审批和最终批复。
- 不得将零散税票或流水片段包装为完整经营闭环。
- 对场地、库存、订单真实性等事项，若未现场核验必须明确标注。
- 不得为了提升准入率而弱化税票、流水、合同和场地之间的矛盾。

## 信息不足时的处理

- 如果资料不全，先输出准入关注点、补件要求和现场核验重点。
- 如果税票流水和合同无法闭环，不要硬写“经营真实”，应明确标注待核验。
- 如果红旗较多但证据不足，优先给审慎推进和补证据建议。

## 交付标准

- 一线客户经理拿到结果后，可以直接用于继续访谈、补件或是否报送的判断。
- 输出里要清楚区分已确认信息、待核验事项和经验判断。
- 至少回答三个问题：这家客户现在怎么看、为什么这么看、下一步怎么做。
