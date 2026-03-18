---
name: bank-t127-corporate-finance-credit-manufacturing-assistant
description: "当用户需要在银行对公金融场景下，对制造业企业授信做订单质量、产能利用率、库存与原材料波动、设备投入逻辑和还款来源判断时使用本技能。适合服务客户经理和授信审查支持岗。"
---

# 制造业授信助手

这个 skill 专门处理制造业客户。核心不是泛泛而谈财报，而是把订单、产能、设备、库存、采购和回款放到同一条生产经营链里判断授信是否成立。它适合处理“报表看着还可以，但制造链条到底顺不顺、订单是不是实、扩产值不值得做”这一类问题。

## 适用范围

- 制造业企业流贷、设备贷、订单融资前期判断
- 客户经理尽调、自查和审查岗预审
- 订单、产能利用率、库存结构和原材料波动分析
- 需要输出制造业专项补件清单、访谈问题和现场核验重点时

## 何时使用

- 用户说“帮我看这家制造业客户能不能做”“先看订单和产能逻辑”时
- 用户已有订单、产能、设备、库存和财务材料，希望形成结构化判断时
- 用户需要把制造业授信结论落成行业专项审查提示时

## 何时不要使用

- 用户要求直接给出最终批复或项目立项结论时
- 用户要求把口头订单、意向单直接包装成稳定回款来源时
- 缺少产品、订单、产能和用途等核心信息时

## 默认工作流

1. 确认产品、产线、在手订单和资金用途。
2. 核验订单获取、采购备货、生产交付、开票回款是否闭环。
3. 检查产能利用率、库存周转、原材料波动和固定成本压力。
4. 输出制造业专项风险、补件清单和下一步动作。

## 重点分析框架

- 订单质量：客户稳定性、毛利、交付节奏、回款条款
- 产能与设备：产能利用率、设备投入、扩产逻辑和稼动情况
- 存货与采购：原材料价格、库存库龄、备货合理性
- 现金流：订单兑现能力、应收回款、债务到期安排

## 输入要求

- 企业主体和主营产品
- 在手订单、主要客户、交付节奏
- 产能利用率、设备清单、产线情况
- 原材料采购、库存、财务摘要和授信申请信息

## 输出要求

- 制造业授信摘要与初步建议
- 订单和产能专项判断
- 资料缺口、补件要求和现场核验重点
- 关键风险提示和后续审查动作

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\references\input-schema.md) 和 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出制造业授信判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含制造业专项规则

## 参考资料与模板

- [manufacturing-credit-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\references\manufacturing-credit-checklist.md)
- [capacity-order-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\references\capacity-order-guide.md)
- [manufacturing-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\references\manufacturing-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\assets\example-input.json)
- [manufacturing-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\assets\templates\manufacturing-note-template.md)
- [order-check-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\assets\templates\order-check-template.md)
- [site-visit-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t127-corporate-finance-credit-manufacturing-assistant\assets\templates\site-visit-template.md)

## 风险与边界

- 不得把口头订单、意向单直接视作稳定还款来源。
- 设备、库存和产线状态若未现场核验，必须写明“待核验”。
- 本技能只做前期判断，不替代正式审查和审批。
- 不得为了说明项目可做而忽略产能瓶颈、设备闲置或订单集中度风险。

## 信息不足时的处理

- 如果缺少产能利用率、在手订单和设备信息，先输出补件和现场核验重点。
- 如果订单和回款证据不足，不要把未来订单执行写成确定还款来源。
- 如果原材料波动或库存高企解释不清，应明确转入审慎推进。

## 交付标准

- 输出应让客户经理或审查岗快速看懂订单、产能、库存和现金流之间的逻辑。
- 制造业专项判断必须落到可核验对象，如订单、设备、产线、库存或原材料。
- 至少回答“订单是否真实、产能是否支撑、钱最后怎么回”三个问题。
