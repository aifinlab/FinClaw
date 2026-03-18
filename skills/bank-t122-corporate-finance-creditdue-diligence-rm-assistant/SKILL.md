---
name: bank-t122-corporate-finance-creditdue-diligence-rm-assistant
description: "当用户需要在银行对公金融场景下，以客户经理视角推进企业授信尽调、整理资料清单、设计访谈提纲、识别现场核查重点、形成风险假设和输出尽调纪要时使用本技能。适合输出能直接支持客户拜访和授信推进的尽调包。"
---

# 企业授信尽调助手-客户经理版

这个 skill 面向一线客户经理使用。它不是审查岗的终审工具，也不是审批会的拍板工具，而是帮助客户经理把授信尽调从“到处找材料、临时想问题”变成一套可执行的推进动作。

它优先解决五类问题：

1. 客户经理这次去访谈和尽调，最该问什么
2. 现有材料还缺什么，补件顺序怎么排
3. 现场尽调最该看哪些地方
4. 当前项目的风险假设是什么，下一步该怎么验证
5. 如何把尽调过程沉淀成一份能往内部流转的结构化纪要

## 适用范围

- 新增授信项目的客户经理尽调准备
- 已报送项目的补充尽调与再访谈
- 续授信、增额、展期前的一线客户复核
- 需要输出访谈提纲、补件清单、现场核查重点、尽调纪要时
- 需要把零散企业信息整理为“客户经理可执行动作包”时

## 何时使用

- 用户说“帮我准备明天去客户那里尽调”“帮我列访谈问题”“帮我整理客户经理尽调清单”时
- 用户已经拿到部分财务、合同、流水、工商信息，但还不知道尽调动作先后顺序时
- 用户需要写客户经理版尽调纪要、问题清单、补件通知、现场核查要点时
- 用户希望先把风险假设列出来，再决定下一步找什么证据验证时

## 何时不要使用

- 用户要求直接输出最终授信审批意见、最终批复结论时
- 用户要求伪造尽调记录、包装客户陈述、隐瞒重大风险时
- 需要法律、审计、评估等专项专业结论才能定性的场景
- 用户只需要纯行业研究，而不涉及具体授信客户尽调动作时

## 默认工作流

1. 先明确本次尽调目标，是新增授信、补件尽调、贷后回访还是续作复核。
2. 把现有信息按主体、业务、财务、用途、担保、外部风险六类归集。
3. 先产出补件清单，再产出访谈提纲，再产出现场核查重点。
4. 针对高风险假设设计验证动作，不要只停留在“有风险”三个字。
5. 输出客户经理尽调纪要，明确已确认、待核验和待补充三类事项。
6. 给出下一步推进建议，包括补件、复访、升级审查或暂缓推进。

## 客户经理版核心分析框架

### 1. 客户到底是不是“说得清、看得见、对得上”

- 企业主体、股权、管理层是否说得清
- 业务模式、订单、回款和流水是否对得上
- 财务数据、现场情况和客户陈述是否能互相印证

### 2. 这笔授信为什么要做，现在为什么要做

- 客户需求是否真实
- 申请金额和期限是否与周转逻辑匹配
- 用途和还款来源是否能被一线拿到证据支撑

### 3. 现场最该看的是什么

- 生产经营是否真实存在
- 客户、供应商、仓库、设备、库存、回款单据是否有重点异常
- 管理层对关键问题能否自洽回答

### 4. 当前最可能踩雷的地方是什么

- 主体和治理异常
- 业务真实性不足
- 现金流与利润背离
- 对外担保、涉诉、舆情、关联交易
- 增信措施“写得好看但落不到实处”

## 输入要求

建议尽量提供：

- 企业基础资料：企业名称、行业、区域、成立年限、股权结构、实控人
- 授信申请信息：品种、金额、期限、用途、增信方式
- 财务与经营信息：收入、利润、现金流、订单、合同、发票、流水、纳税信息
- 外部风险信息：工商变更、涉诉处罚、舆情、历史逾期、担保链风险
- 当前材料状态：已经拿到什么、还缺什么、哪些材料客户口头说有但未提供
- 本次尽调目标：访谈、补件、现场核查、纪要输出、内部汇报

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\references\input-schema.md)。

## 输出要求

默认输出至少应包含：

1. 本次尽调目标与项目概况
2. 已掌握资料与关键信息缺口
3. 客户经理补件清单
4. 管理层访谈提纲
5. 现场核查重点
6. 初步风险假设
7. 需向内部审查提前提示的问题
8. 尽调纪要或一页纸摘要
9. 下一步推进建议

## 配套脚本

- `scripts/corporate_credit_dd_rm.py`：生成客户经理版尽调动作包
- `scripts/run_skill.py`：脚本入口

示例调用：

```bash
python scripts/run_skill.py --input assets/example-input.json --output dd_packet.md --format markdown
```

## 参考资料与模板

- [due-diligence-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\references\due-diligence-checklist.md)
- [management-interview-outline.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\references\management-interview-outline.md)
- [field-visit-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\references\field-visit-guide.md)
- [risk-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\references\risk-red-flags.md)
- [due-diligence-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\assets\templates\due-diligence-note-template.md)
- [interview-outline-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\assets\templates\interview-outline-template.md)
- [supplement-list-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t122-corporate-finance-creditdue-diligence-rm-assistant\assets\templates\supplement-list-template.md)

## 风险与边界

- 本技能输出的是客户经理尽调动作和初步判断，不是最终授信审批意见。
- 不得把客户口头陈述直接包装成“已核实事实”。
- 不得为了推进业务淡化重大风险、虚构材料或跳过关键核查动作。
- 对仍未核验的事项必须明确标注“待核验”“待补证据”。
- 对需要外部权威核验的事项，应明确建议升级给审查、法务或专项核查。

## 信息不足时的处理

- 如果材料少，就先输出补件清单和访谈提纲，不要强写完整尽调结论。
- 如果行业和业务逻辑没看懂，就把现场核查重点和需客户说明的问题排在最前面。
- 如果已经出现明显红旗，应把“先别急着推进，先核实什么”写清楚。

## 交付标准

- 客户经理拿到输出后，能直接带着去见客户或整理内部报送材料。
- 补件、访谈、现场核查、内部提示四类动作都要落到可执行层。
- 能区分一线已确认信息、客户陈述信息和仍需后续核验的信息。
