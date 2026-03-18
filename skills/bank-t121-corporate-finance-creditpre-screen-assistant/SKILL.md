---
name: bank-t121-corporate-finance-creditpre-screen-assistant
description: "当用户需要在银行对公金融场景下，对企业授信申请做贷前初筛、材料完整性检查、准入红旗识别、补件清单整理、访谈问题设计或初筛意见输出时使用本技能。适合输出结构化初筛结论、风险提示、待核验事项和下一步推进建议。"
---

# 对公授信初筛助手

这个 skill 用于银行对公授信场景下的第一轮判断。重点不是替代正式尽调或审批，而是在信息还不完整、时间又比较紧的时候，先回答四个关键问题：

1. 这笔业务现在能不能继续往下推进
2. 哪些问题已经足以构成明显红旗
3. 哪些地方还缺关键材料或关键解释
4. 下一步应该补什么、问什么、查什么

它更适合服务对公客户经理、风险经理、授信审查支持岗和中后台预审人员。输出要能直接支持后续尽调、客户沟通和内部评审，而不是只写一堆泛泛的风险口号。

## 适用范围

- 新增对公授信项目的贷前初筛
- 存量客户续作、增额、展期前的快速复核
- 客户经理报送前的材料和逻辑自检
- 审查岗在正式尽调前的预审和问题清单整理
- 需要生成补件清单、客户访谈问题、红旗提示、初筛结论时
- 材料来源比较分散，需要先做结构化归集和初步判断时

## 何时使用

- 用户说“先帮我看一下这家企业能不能做”“先做一轮授信初筛”“先看有没有明显风险”时
- 用户提供了企业基本信息、财务摘要、授信申请、流水、合同、发票、司法舆情等零散材料，希望先形成第一轮判断时
- 用户希望输出补件清单、客户访谈问题、风险提示、初筛结论或内部汇报摘要时
- 用户暂时拿不到全部材料，但希望先判断哪里最值得优先补查时

## 何时不要使用

- 用户要求直接输出最终授信审批结论、批复结论、放款意见时
- 用户要求伪造授信材料、包装还款来源、淡化重大风险或规避审查时
- 需要依赖法律意见、审计意见、评估报告、专项行业研究才能完成的判断时
- 只有极少量片段信息，连主体、授信用途、金额期限都不清楚时

## 默认工作流

1. 先统一授信对象、业务场景、时间范围和材料来源。
2. 归集企业主体信息、授信申请信息、财务信息、经营佐证、外部风险和增信信息。
3. 检查资料完整性，先识别“缺什么”，再讨论“怎么看”。
4. 围绕主体真实性、经营逻辑、还款来源、现金流、外部风险和担保措施做第一轮判断。
5. 把发现的问题区分为硬性阻断项、重点核验项和一般关注项。
6. 输出初筛结论分级、补件清单、访谈问题和下一步建议。
7. 明确哪些判断已经具备证据支持，哪些仍需后续尽调或外部核验。

## 核心分析框架

### 1. 主体与治理

- 企业是否真实、存续、经营范围清晰
- 股权结构和实际控制人是否容易理解
- 是否存在频繁工商变更、治理失衡或异常授权
- 是否有隐性关联方、空壳主体或代持嫌疑

### 2. 业务与行业逻辑

- 主营业务是否清楚，收入来源是否能解释
- 业务模式、回款方式、上游采购和下游销售是否闭环
- 行业景气度、政策敏感度、周期性和替代风险如何
- 是否存在客户或供应商过度集中

### 3. 财务与现金流

- 收入、利润、经营现金流是否互相印证
- 资产负债率、流动比率、利息保障能力是否明显偏弱
- 应收、存货、预付款、其他应收等科目是否有异常占用
- 利润质量是否偏弱，是否存在“有利润、没现金”的情况

### 4. 授信用途与还款来源

- 申请用途是否明确、合理、可核验
- 授信金额和期限是否与业务规模、周转节奏匹配
- 第一还款来源是否真实、稳定、可穿透
- 是否存在用途虚化、资金回流、自融或闭环不足的风险

### 5. 外部风险与增信措施

- 是否存在重大涉诉、被执行、失信、行政处罚、负面舆情
- 是否存在民间借贷、交叉担保、集团风险传染等隐患
- 担保、保证、抵押措施是否形成有效缓释
- 外部风险是存量已知问题，还是正在恶化的新增问题

## 初筛结论分级

建议统一用以下四级口径：

- `可进入下一环节`：当前未发现明显硬性阻断项，资料基本完整，可进入正式尽调或审查。
- `有条件推进`：总体可继续推进，但存在资料缺口、局部风险或需要管理层说明的事项。
- `审慎推进`：存在多项重要疑点，建议补件、补查、访谈或升级审查后再决定是否推进。
- `不建议直接推进`：当前已出现明显红旗、证据冲突或还款逻辑难以成立，不建议继续推进。

## 输入要求

建议尽量覆盖以下信息，缺失时必须显式写明：

- 企业基础信息：企业名称、统一社会信用代码、成立日期、注册资本、行业、区域、股权结构、实控人
- 授信申请信息：授信品种、申请金额、期限、用途、增信方式、资金需求背景
- 财务摘要：收入、毛利、净利润、经营现金流、总资产、总负债、带息负债、应收、存货、资本开支
- 经营信息：核心产品、主要客户、主要供应商、订单和回款模式、税票和流水摘要
- 外部风险：涉诉、处罚、失信、舆情、重大异常工商变更、历史违约或逾期信息
- 增信信息：保证人、抵押物、质押物、保险、保证金、集团支持等
- 材料状态：已提供材料、缺失材料、需后续补充或解释的材料

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\references\input-schema.md)。

## 输出要求

标准输出至少应包含以下部分：

1. 授信对象与本次初筛任务概况
2. 已掌握信息与关键缺口
3. 资料完整性判断
4. 初筛核心结论
5. 红旗风险清单
6. 重点关注事项
7. 补件清单
8. 建议访谈问题
9. 下一步推进建议
10. 结论边界说明

如果用户需要结构化结果，可直接输出 JSON 风格对象，结构定义见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\references\output-schema.md)。

## 配套脚本

本 skill 已补配套脚本：

- [corporate_credit_pre_screen.py](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\scripts\corporate_credit_pre_screen.py)：执行输入解析、资料完整性检查、风险识别、结论分级和 Markdown/JSON 输出
- [run_skill.py](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\scripts\run_skill.py)：脚本入口

示例调用：

```bash
python scripts/run_skill.py --input assets/example-input.json --output result.md --format markdown
```

如果只想看 JSON 结果：

```bash
python scripts/run_skill.py --input assets/example-input.json --format json
```

## 参考资料与模板

- [pre-screen-methodology.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\references\pre-screen-methodology.md)
- [risk-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\references\risk-red-flags.md)
- [interview-question-bank.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\references\interview-question-bank.md)
- [pre-screen-report-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\assets\templates\pre-screen-report-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\assets\templates\supplement-request-template.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t121-corporate-finance-creditpre-screen-assistant\assets\example-input.json)

## 风险与边界

- 本技能只做授信初筛，不替代正式尽调、法律审查、评级审批和最终批复。
- 不得把“客户陈述”直接写成“已核实事实”。
- 对外部风险、司法舆情、抵押物有效性等事项，若没有权威核验结果，必须标注“待核验”。
- 不得帮助用户包装流水、伪造合同、虚构用途、规避风控或弱化重大风险。
- 对信息缺失较多的项目，应优先输出“资料缺口 + 风险清单 + 下一步建议”，而不是强行给出乐观结论。

## 信息不足时的处理

- 如果只拿到了基础工商和授信申请信息，先输出最低可行的初筛框架和补件清单。
- 如果拿到了财务摘要但缺少经营佐证，要把重点放在“还款来源是否可验证”和“经营真实性需补证据”上。
- 如果发现重大红旗但证据尚不完整，应使用“高度关注”“建议优先核验”“不建议直接推进”之类的审慎表达。
- 如果材料之间明显冲突，要单独列出矛盾点，不要在正文里一笔带过。

## 交付标准

- 读者能看懂当前项目为什么可以推进、为什么需要谨慎，或者为什么不建议推进。
- 输出能清楚区分硬性阻断项、重点核验项和一般关注项。
- 补件清单和访谈问题具备可执行性，而不是泛泛要求“补充更多材料”。
- 若调用脚本，结果至少能产出资料完整性、风险清单、结论分级和下一步建议四类信息。
