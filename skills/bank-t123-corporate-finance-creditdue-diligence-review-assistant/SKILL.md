---
name: bank-t123-corporate-finance-creditdue-diligence-review-assistant
description: "当用户需要在银行对公金融场景下，对企业授信项目生成审查要点、拆解关键疑点、整理补充核验要求并形成审查岗可直接使用的结构化审阅框架时使用本技能。适合输出授信审查关注点、证据缺口、风险缓释要求和初步审查建议。"
---

# 对公授信审查要点生成助手

这个 skill 面向授信审查、审查支持、授信秘书或需要从审查视角复核材料的人使用。它的目标不是直接替代终审结论，而是把一笔对公授信项目拆成一套清楚、可追踪、可补证据的审查要点包。

它优先解决六类问题：

1. 这笔项目当前最核心的审查关注点是什么
2. 哪些问题属于硬性阻断项，哪些只是待核验项
3. 现有材料之间有哪些不一致或证据缺口
4. 审查岗还需要客户经理补什么、核什么、解释什么
5. 风险缓释条件应该往哪里补强
6. 如何快速整理成审查纪要、审查提示或上会前的一页纸

## 适用范围

- 对公新增授信项目的审查要点整理
- 企业授信补充审查、复审、续作复核
- 对客户经理已完成的尽调材料做二次结构化审阅
- 需要形成授信审查关注点、补件要求、审查提问清单时
- 需要把零散财务、合同、流水、外部风险信息整理成审查岗工作底稿时

## 何时使用

- 用户说“帮我梳理授信审查要点”“帮我列审查岗关注点”“帮我做上会前的审查提示”时
- 用户已经有尽调材料，但需要换到审查视角重新拆解风险和证据链时
- 用户需要把项目分成准入前提、业务真实性、用途、还款来源、增信、外部风险几个审查模块时
- 用户需要结构化输出补件清单、待核验事项和初步审查建议时

## 何时不要使用

- 用户要求直接给出最终批复结论、放款结论或绕过正式审批流程时
- 用户要求隐瞒重大风险、弱化疑点或把未核事实写成已核实时
- 缺少最基本项目资料，连申请主体、金额、用途、还款来源都不明确时
- 需要法律、评估、审计等专项结论才能定性的事项，但用户又要求本技能直接替代专业判断时

## 默认工作流

1. 先确认授信项目基本盘，包括申请主体、金额、期限、用途、还款来源和增信方式。
2. 按审查视角拆成六个模块：准入前提、业务真实性、财务与现金流、债务与担保、增信有效性、外部风险。
3. 标出硬性阻断项、重点核验项和一般关注项，不要把所有问题混成一类。
4. 检查材料之间是否一致，重点看财报、流水、合同、发票、工商司法信息是否能互相印证。
5. 对每个关键风险点给出补件要求、核验动作和缓释方向，而不是只说“有风险”。
6. 输出审查要点包，明确当前结论只能是初步审查意见，不替代最终审批结论。

## 审查岗核心分析框架

### 1. 准入前提是否成立

- 主体是否合法合规，经营资格是否完整
- 行业、区域、产品、交易背景是否触及明显禁限入规则
- 授信申请是否与企业规模、经营阶段和存量负债水平基本匹配

### 2. 业务与融资逻辑是否闭环

- 企业到底做什么，靠什么赚钱，收入是否真实可解释
- 本次融资为什么需要做，为什么是这个金额和期限
- 用途、订单、采购、生产、交付、回款能否串成闭环

### 3. 还款来源和现金流是否可靠

- 第一还款来源是否可量化、可验证、可追踪
- 利润、现金流、应收、存货、债务压力之间是否匹配
- 是否存在借新还旧、依赖续贷、现金流弱于利润等问题

### 4. 增信和缓释措施是否真正可落地

- 保证人是否真有代偿能力
- 抵押、质押物是否权属清晰、价值可接受、处置路径明确
- 封闭回款、确权、监管账户等控制措施是否真的能执行

### 5. 外部风险是否已经影响授信可行性

- 涉诉、处罚、舆情、异常工商变更是否构成实质障碍
- 关联交易、交叉担保、实际控制人风险是否会穿透到申请主体
- 历史逾期、征信异常、非标融资依赖是否值得升级审查

## 输入要求

建议尽量提供：

- 企业主体信息：名称、行业、区域、成立年限、股东结构、实控人、核心管理层
- 授信申请信息：品种、金额、期限、用途、提款节奏、还款来源、增信方案
- 财务信息：收入、利润、经营现金流、资产负债、应收、存货、有息负债
- 业务材料：主要客户供应商、订单、合同、发票、纳税、回款流水
- 风险材料：涉诉、处罚、舆情、担保链、历史逾期、征信或授信存量
- 材料状态：哪些已提供，哪些缺失，哪些口头说明但未给证据
- 审查目标：要输出审查要点、补件单、审查提问单、上会前提示还是审查摘要

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\references\input-schema.md)。

## 输出要求

默认输出至少应包含：

1. 项目概况与当前审查阶段
2. 硬性阻断项、重点核验项、一般关注项
3. 证据缺口与材料不一致点
4. 补充核验要求
5. 审查提问要点
6. 风险缓释建议
7. 初步审查建议与后续动作
8. 可直接流转的审查摘要或一页纸

## 配套脚本

- `scripts/corporate_credit_review_points.py`：生成对公授信审查要点包
- `scripts/run_skill.py`：脚本入口

示例调用：

```bash
python scripts/run_skill.py --input assets/example-input.json --output review_points.md --format markdown
```

## 参考资料与模板

- [review-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\references\review-checklist.md)
- [evidence-standards.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\references\evidence-standards.md)
- [review-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\references\review-red-flags.md)
- [review-memo-framework.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\references\review-memo-framework.md)
- [review-points-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\assets\templates\review-points-template.md)
- [supplement-request-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\assets\templates\supplement-request-template.md)
- [review-brief-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t123-corporate-finance-creditdue-diligence-review-assistant\assets\templates\review-brief-template.md)

## 风险与边界

- 本技能输出的是审查要点和初步审阅意见，不是最终授信批复或审批会结论。
- 未经核验的客户口径、客户经理描述和外部传闻，不得直接写成已确认事实。
- 不得为了推动业务而有意淡化疑点、跳过重要核验或包装证据链。
- 对无法定性的事项，应明确标记为“待核验”“待补证据”“建议升级专项审查”。
- 对法律、评估、审计、押品价值等专项事项，应建议转交相应专业岗位判断。

## 信息不足时的处理

- 如果资料不全，先输出审查关注点、补件清单和待核验动作，不要强行写确定性结论。
- 如果业务逻辑还没看懂，优先把用途、回款来源、合同闭环和资金流向列为一类重点核验事项。
- 如果已经出现明显红旗，先把阻断项和升级审查建议写清楚，再谈下一步推进。

## 交付标准

- 审查岗拿到输出后，可以直接用于继续审阅、要求补件或准备上会前提示。
- 输出中必须清楚区分事实、疑点、假设和建议动作。
- 每个关键问题尽量带上“为什么关注”“需要补什么”“怎么验证”。
- 结果要能回答四个问题：现在看到什么、哪里不够、风险在哪、下一步怎么做。
