---
name: bank-t130-corporate-finance-credit-soe-assistant
description: "当用户需要在银行对公金融场景下，对国企客户授信做股权层级、主责主业、集团支持边界、治理授权和资金用途适配性判断时使用本技能。适合服务客户经理和授信审查支持岗。"
---

# 国企授信助手

这个 skill 用于国企客户授信判断。重点不是笼统地说“国企比较稳”，而是识别股权层级、主责主业、内部决策程序和上级支持边界，避免把背景误当成无条件担保。它适合处理“国企背景看起来强，但究竟是谁支持、支持到什么程度、有没有合规授权”的问题。

## 适用范围

- 国企、地方国资企业、产业类国企授信前期判断
- 主责主业、股权链条、内部治理与授权核验
- 上级支持边界和融资用途匹配性分析
- 需要输出国企专项补件清单、核验重点和推进建议时

## 何时使用

- 用户说“帮我看这家国企能不能做”“先拆股权层级和上级支持边界”时
- 用户已有股权链、支持文件、主责主业和融资材料，希望形成结构化判断时
- 用户需要把国企授信结论落成客户经理或审查岗可用的专项提示时

## 何时不要使用

- 用户要求把国资背景直接当作刚性担保或最终审批理由时
- 用户要求跳过授权、决策程序和支持文件核验时
- 核心股权链条、上级单位信息和融资用途都不清楚时

## 默认工作流

1. 梳理股权层级、实控链条和主责主业。
2. 核验本次融资用途是否符合企业定位和内部授权要求。
3. 判断上级支持是制度性、项目性还是口径性支持。
4. 输出国企专项判断、补件要求和推进建议。

## 输入要求

- 企业主体、股权链条、上级单位信息
- 主责主业、经营板块、融资申请信息
- 董事会/党委会/授权文件、上级支持材料
- 财务摘要、担保安排、涉诉和外部风险信息

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\references\input-schema.md)。

## 输出要求

- 国企授信摘要与初步建议
- 股权层级和上级支持边界判断
- 资料缺口、补件要求和核验重点
- 风险提示和下一步动作

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出国企授信判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含国企专项规则

## 参考资料与模板

- [soe-credit-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\references\soe-credit-checklist.md)
- [support-boundary-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\references\support-boundary-guide.md)
- [soe-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\references\soe-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\assets\example-input.json)
- [soe-credit-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\assets\templates\soe-credit-note-template.md)
- [authorization-check-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\assets\templates\authorization-check-template.md)
- [support-matrix-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t130-corporate-finance-credit-soe-assistant\assets\templates\support-matrix-template.md)

## 风险与边界

- 不得把国资背景、股东名称或历史合作直接写成刚性兜底。
- 对授权、决策程序和支持文件未核验的事项，必须标注“待核验”。
- 本技能不替代正式集团授信审查或最终审批。
- 对上级支持边界的判断必须回到文件、制度和决策程序，不得依据主观印象外推。

## 信息不足时的处理

- 如果股权层级、主责主业和支持文件不全，先输出补件清单和核验重点。
- 如果支持依据只有口头表态，应明确写为待核验，不得写成确定支持。
- 如果治理授权链条不清，优先给出审慎推进或升级审查建议。

## 交付标准

- 输出必须把“谁控制、谁决策、谁支持、支持到哪里”写清楚。
- 关键判断应能支撑客户经理继续访谈或审查岗进一步核验。
- 至少回答三个问题：这家国企为什么能看、哪些地方不能想当然、下一步怎么补证据。
