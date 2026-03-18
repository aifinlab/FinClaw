---
name: bank-t131-corporate-finance-credit-private-enterprise-assistant
description: "当用户需要在银行对公金融场景下，对民企客户授信做实控人稳定性、资金链韧性、股权质押、对外担保和关联风险穿透判断时使用本技能。适合服务客户经理和授信审查支持岗。"
---

# 民企授信助手

这个 skill 面向民企授信判断。核心是把企业信用和实控人信用放在一起看，识别资金链、对外担保、股权质押和关联交易等容易导致风险突变的因素。它适合处理“业务看起来不错，但实控人和外部担保链到底稳不稳”的问题。

## 适用范围

- 民企、家族企业、成长型企业授信前期判断
- 实控人稳定性、对外担保、股权质押和关联风险排查
- 客户经理尽调、审查支持和复核准备
- 需要输出民企专项补件要求、风险提示和推进建议时

## 何时使用

- 用户说“帮我看这家民企能不能做”“先看实控人和资金链风险”时
- 用户已有实控人、股权质押、担保和经营资料，希望形成结构化判断时
- 用户需要把民企风险拆成企业层、个人层和关联链条层时

## 何时不要使用

- 用户要求以个人口碑或非正式承诺替代信用判断时
- 用户要求忽略对外担保、股权质押或关联风险时
- 缺少实控人信息、用途和还款来源时

## 默认工作流

1. 确认企业主体、实控人、融资申请和主要经营逻辑。
2. 核验实控人稳定性、股权质押、对外担保和关联往来。
3. 判断经营现金流、融资依赖度和备用还款能力。
4. 输出民企专项判断、补件清单和后续动作。

## 输入要求

- 企业主体、实控人、股权结构
- 申请金额、用途、期限和第一还款来源
- 财务摘要、存量授信、主要客户与供应商
- 股权质押、对外担保、涉诉、或有负债和关联交易信息

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\references\input-schema.md)。

## 输出要求

- 民企授信摘要与初步建议
- 实控人和资金链稳定性判断
- 资料缺口、补件要求和核验重点
- 风险提示和后续推进建议

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出民企授信判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含民企专项规则

## 参考资料与模板

- [private-enterprise-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\references\private-enterprise-checklist.md)
- [controller-risk-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\references\controller-risk-guide.md)
- [private-enterprise-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\references\private-enterprise-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\assets\example-input.json)
- [private-enterprise-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\assets\templates\private-enterprise-note-template.md)
- [controller-check-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\assets\templates\controller-check-template.md)
- [guarantee-chain-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t131-corporate-finance-credit-private-enterprise-assistant\assets\templates\guarantee-chain-template.md)

## 风险与边界

- 不得把个人口碑、非正式承诺或口头担保写成有效信用缓释。
- 对实控人资产负债、对外担保、股权质押等事项，若未核实必须明确说明。
- 本技能只做前期判断，不替代正式授信审批和最终批复。
- 不能因为企业经营表现尚可，就忽略实控人和关联链条的潜在突发风险。

## 信息不足时的处理

- 如果实控人、质押、担保和关联交易信息不全，先生成补件和穿透核验清单。
- 如果存在高风险线索但证据不足，应明确给出待核验提示，不做强结论。
- 如果担保链和资金链压力解释不清，默认转入审慎推进。

## 交付标准

- 输出要能把企业信用和实控人信用放在一起看，而不是割裂判断。
- 风险应落到实控人、股权质押、对外担保和关联链条等具体对象。
- 至少回答“企业本身怎么看、实控人怎么看、风险怎么传导”三个问题。
