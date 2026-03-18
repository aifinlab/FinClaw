---
name: bank-t129-corporate-finance-credit-platform-assistant
description: "当用户需要在银行对公金融场景下，对平台企业授信做财政依赖度、市场化现金流、政府支持边界、隐性债务压力和持续融资能力判断时使用本技能。适合服务政府融资平台相关客户经理和审查人员。"
---

# 平台企业授信助手

这个 skill 重点处理平台企业授信。判断核心不是“有没有国资背景”，而是平台自身经营现金流是否独立、财政支持边界是否清楚、隐性债务压力是否可控，以及融资安排是否过度依赖续借和政府兜底口径。

## 适用范围

- 政府融资平台及类平台企业授信前期判断
- 财政依赖度、市场化业务收入和债务结构拆分
- 政府购买服务、公益性项目与经营性项目混合场景分析
- 需要输出平台专项判断、补件要求和升级审查提示时

## 何时使用

- 用户说“帮我看这家平台企业能不能做”“先拆财政依赖和市场化现金流”时
- 用户已有平台定位、政府购买服务合同、债务结构和融资需求材料，希望先做结构化判断时
- 用户需要把平台融资风险拆到财政、经营、隐债和支持边界四层时

## 何时不要使用

- 用户要求把“平台背景”直接写成无风险背书时
- 用户要求编造财政支持、承诺函或隐债化解安排时
- 缺少财政依赖度、市场化收入和债务结构等关键材料时

## 默认工作流

1. 确认平台定位、股权背景、申请融资结构。
2. 拆分财政性收入和市场化经营现金流。
3. 判断政府支持边界、隐性债务压力和债务续接能力。
4. 输出平台专项判断、补件要求和下一步动作。

## 重点分析框架

- 平台定位：公益性任务、经营性业务、区域地位
- 现金流结构：财政拨付、政府购买服务、市场化收入、自主经营能力
- 债务压力：存量债务、到期安排、再融资依赖和隐性债务风险
- 支持边界：股东支持、财政支持、政策口径和可执行性

## 输入要求

- 企业主体、股东背景、区域定位
- 申请金额、用途、期限、还款来源
- 财政依赖度、市场化收入拆分、政府购买服务合同
- 存量债务、到期结构、外部政策和隐性债务信息

## 输出要求

- 平台授信摘要与初步建议
- 财政依赖度和市场化现金流判断
- 资料缺口、补件清单和专项核验点
- 风险提示和推进/升级动作

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\references\input-schema.md) 和 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出平台企业授信判断包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含平台专项规则

## 参考资料与模板

- [platform-credit-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\references\platform-credit-checklist.md)
- [fiscal-market-cashflow-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\references\fiscal-market-cashflow-guide.md)
- [platform-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\references\platform-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\assets\example-input.json)
- [platform-credit-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\assets\templates\platform-credit-note-template.md)
- [cashflow-split-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\assets\templates\cashflow-split-template.md)
- [support-boundary-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t129-corporate-finance-credit-platform-assistant\assets\templates\support-boundary-template.md)

## 风险与边界

- 不得将“平台背景”直接等同于无风险或刚性支持。
- 对财政支持、政府付款和债务承接安排，如无正式文件不得写成确定事实。
- 本技能只做分析支持，不替代正式政策认定和审批判断。
- 对政府支持、区域财政承受力和隐性债务的判断，必须明确证据来源和边界。

## 信息不足时的处理

- 如果财政依赖度、市场化收入拆分和到期债务结构缺失，先输出补件清单。
- 如果政府支持依据只有口头说明，应明确标记为待核验。
- 如果隐性债务压力无法评估，默认以审慎推进表达，不给过强结论。

## 交付标准

- 输出应把财政性收入、市场化收入和债务续接逻辑拆清楚。
- 支持边界必须区分“已有文件支持”和“仅市场预期支持”。
- 至少回答“谁来还、靠什么还、支持能到哪一步”三个问题。
