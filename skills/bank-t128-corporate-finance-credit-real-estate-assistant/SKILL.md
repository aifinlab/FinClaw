---
name: bank-t128-corporate-finance-credit-real-estate-assistant
description: "当用户需要在银行对公金融场景下，对房地产企业或项目授信做项目去化、受限资金、债务到期压力、销售回款和政策合规约束判断时使用本技能。适合服务客户经理和地产审查岗。"
---

# 房地产授信助手

这个 skill 面向房地产授信，不把“地产背景”当成抽象标签，而是按项目、资金和债务三个层面拆开判断。重点看项目能否卖、钱能否回、债能否还，以及政策和手续是否让这个项目具备继续推进的基础。

## 适用范围

- 房地产开发贷、经营性物业融资、存量地产客户复核
- 项目去化、受限资金、销售回款、债务错配分析
- 地产客户准入前梳理和风险预审
- 需要输出项目维度判断、专项补件清单和风险提示时

## 何时使用

- 用户说“帮我看这家地产客户能不能上”“先看项目去化和资金情况”时
- 用户有项目清单、销售去化、受限资金和债务结构材料，希望先做结构化判断时
- 用户需要把地产风险拆成项目、资金、债务和政策四层时

## 何时不要使用

- 用户要求直接给出最终审批或政策认定结论时
- 用户要求把预期销售、口径化回款写成确定现金流时
- 核心项目清单、去化和受限资金都缺失时

## 默认工作流

1. 统一主体、项目清单、申请金额和授信用途。
2. 核验项目分布、销售去化、受限资金和现金回笼节奏。
3. 评估短中期债务到期、项目续建和政策合规压力。
4. 输出地产专项判断、补件清单和推进建议。

## 重点分析框架

- 项目层面：项目区位、去化速度、销售签约、回款节奏
- 资金层面：受限资金、可自由支配现金、监管账户安排
- 债务层面：公开债、非标、开发贷和未来到期峰值
- 合规层面：开发资质、政策约束、项目手续和销售限制

## 输入要求

- 企业主体、项目清单、区域分布
- 申请金额、用途、期限和还款来源
- 项目销售去化、受限资金、可支配现金和债务结构
- 外部政策压力、涉诉舆情和重大合规事项

## 输出要求

- 地产授信摘要与初步建议
- 项目去化和资金覆盖判断
- 资料缺口、补件清单和专项核验点
- 关键风险提示和后续推进动作

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\references\input-schema.md) 和 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出房地产授信判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含地产专项规则

## 参考资料与模板

- [real-estate-credit-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\references\real-estate-credit-checklist.md)
- [project-cashflow-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\references\project-cashflow-guide.md)
- [real-estate-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\references\real-estate-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\assets\example-input.json)
- [project-summary-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\assets\templates\project-summary-template.md)
- [debt-maturity-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\assets\templates\debt-maturity-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t128-corporate-finance-credit-real-estate-assistant\assets\templates\supplement-request-template.md)

## 风险与边界

- 不得把预期销售或口径化回款直接当作确定现金流。
- 若项目手续、受限资金或政策约束未核实，必须单列为待核验事项。
- 本技能不替代正式项目审查、评估和最终审批结论。
- 对政策、监管和销售限制的判断，只能基于已确认材料，不得自行臆测外部政策口径。

## 信息不足时的处理

- 如果项目清单、去化和受限资金不完整，优先输出项目维度补件清单。
- 如果现金回笼逻辑高度依赖未来销售，应明确写为待验证假设。
- 如果债务到期峰值和可支配资金覆盖关系不清，默认转入审慎推进。

## 交付标准

- 输出必须让用户一眼看到“项目是否能卖、钱是否能回、债是否能接上”。
- 地产判断尽量按项目维度展开，而不是只给公司层面的笼统评价。
- 关键风险要落到具体变量，如去化、受限资金、手续、到期债务和政策约束。
