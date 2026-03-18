---
name: bank-t125-corporate-finance-due-diligence-post-loan-assistant
description: "当用户需要在银行对公金融场景下，对存量授信客户开展贷后尽调、执行偏差排查、预警信号识别、回访纪要整理或处置建议输出时使用本技能。适合服务贷后管理、风险经理和经营机构，输出结构化监测结论、补件清单、异常信号和后续动作。"
---

# 对公授信贷后尽调助手

这个 skill 面向存量授信的贷后阶段，不做新的准入审批结论，而是帮助用户把“余额、执行、预警、回访、处置”整理成一套可跟踪的贷后动作包。它的重点不是泛泛复述贷后情况，而是尽快识别哪些问题已经发生、哪些问题仍待核验、哪些问题必须升级处置。

## 适用范围

- 存量授信客户贷后检查、回访、复盘
- 经营异常、回款放缓、资金用途偏离、逾期苗头排查
- 贷后台账更新、风险预警、处置建议整理
- 需要输出贷后纪要、预警清单、补件要求和复查计划时
- 需要把一次贷后回访沉淀为结构化结论并纳入持续监测时

## 何时使用

- 用户说“帮我做贷后尽调”“整理这家客户的贷后风险”“输出贷后回访纪要”时
- 用户已掌握贷款余额、最近一次检查结果、经营变化、流水或押品状态，希望形成下一步动作时
- 用户需要区分已发生异常、待确认异常和应持续跟踪事项时
- 用户需要把贷后发现转成预警等级、补件要求和升级建议时

## 何时不要使用

- 用户要求直接给出最终核销、诉讼、重组或审批批复结论时
- 只有零散片段信息，连贷款余额、产品类型、最近检查时间都不清楚时
- 用户要求隐瞒贷后异常、弱化预警或规避风险分类时
- 需要法律诉讼、资产保全部署或正式风险分类结论时

## 默认工作流

1. 统一客户主体、授信余额、产品结构和最近一次贷后检查时点。
2. 对照合同约定、用途约束、财务约束和担保条件检查执行偏差。
3. 识别经营恶化、回款异常、逾期苗头、押品弱化和外部负面事件。
4. 区分已确认异常、待核验异常和持续关注事项。
5. 输出监测结论、补件清单、沟通问题和处置/复查动作。
6. 必要时明确是否进入强化监测、专项核查或升级处置。

## 重点分析框架

- 授信执行：提款、用款、归还、展期、约束条款履行情况
- 经营变化：收入、利润、现金流、订单、客户回款和生产状态
- 风险信号：逾期、涉诉、异常交易、用途偏离、交叉担保、重大负面舆情
- 缓释措施：押品、保证、回款控制、账户监管是否仍然有效
- 处置优先级：继续观察、强化监测、专项核查、升级处置
- 整改闭环：上次检查发现的问题是否已整改，复查证据是否充分

## 输入要求

- 企业主体、存量授信产品、余额、期限、担保方式
- 最近一次贷后检查日期、结论、整改事项
- 财务摘要、经营变化、主要客户和回款情况
- 贷后台账、预警记录、逾期天数、资金用途检查情况
- 押品、保证人、涉诉舆情和异常交易信息

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\references\input-schema.md)。

## 输出要求

- 贷后摘要与当前监测结论
- 关键信息缺口和补件清单
- 已确认/待核验异常信号
- 重点核验要点和客户沟通问题
- 下一步动作、复查节点和升级建议

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：读取输入 JSON，输出 Markdown 或 JSON 的贷后动作包
- `shared/corporate_credit_skill_engine.py`：本批对公授信 skill 共享的分析引擎，内含贷后场景专项规则

示例调用：

```bash
python scripts/run_skill.py --input input.json --format markdown
```

## 参考资料与模板

- [post-loan-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\references\post-loan-checklist.md)
- [post-loan-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\references\post-loan-red-flags.md)
- [post-loan-disposal-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\references\post-loan-disposal-guide.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\assets\example-input.json)
- [post-loan-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\assets\templates\post-loan-note-template.md)
- [warning-summary-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\assets\templates\warning-summary-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t125-corporate-finance-due-diligence-post-loan-assistant\assets\templates\supplement-request-template.md)

## 风险与边界

- 本技能只用于贷后分析和动作安排，不替代风险分类、审批批复或法律处置决定。
- 对资金用途偏离、逾期、担保弱化等事项，若证据不足必须标注“待核验”。
- 不得帮助用户粉饰贷后检查结论、删改异常记录或弱化重大风险。
- 若触发逾期、违约条款或重大舆情，应明确提示升级处置，不得继续给乐观判断。
- 对押品处置、诉讼保全、重组安排等事项，应提示转入相应专业流程。

## 信息不足时的处理

- 先输出已知存量授信和异常线索，再列出缺失字段与复查动作。
- 如果只拿到预警线索但没有证据，优先生成“待核验事项 + 需要补充材料”。
- 对暂时无法确认的异常，不写成既成事实。

## 交付标准

- 输出拿来就能用于一次贷后回访、复查安排或预警沟通。
- 已确认问题、待核验问题和持续跟踪事项必须明确分层。
- 每个风险信号尽量对应“为何关注、补什么、何时复查、是否升级”。
