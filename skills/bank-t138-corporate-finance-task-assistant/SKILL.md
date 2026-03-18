---
name: bank-t138-corporate-finance-task-assistant
description: "当用户需要在银行对公场景下对企业关联方与关联交易做穿透分析（界定边界、归类交易、做合理性测试、穿透资金往来与利润转移、识别风险并形成补件与核验清单）时触发本技能。适合授信尽调/审查/贷后排查的结构化穿透输出。"
---

# 企业关联交易穿透助手

关联交易穿透不是“把关联方名单抄一遍”，而是回答三件事：

1. **边界**：关联方到底有哪些，哪些属于“实质关联”需要纳入分析
2. **交易**：交易的商业合理性是否成立（价格、账期、合同条款、对手方能力）
3. **风险**：是否存在利润转移、资金占用、循环交易、虚增收入或掩盖债务的模式

本 skill 输出的是“可核验、可执行”的穿透包：摘要、缺口、红旗、核验要点、补件清单、访谈问题与下一步动作。它不替代审计/法务结论，也不把穿透结论写成确定性违规定性。

## 适用范围

- 授信尽调/审查：关联交易合理性、资金占用、利润质量、真实现金流识别
- 贷后排查：出现异常往来、资金回流、应收异常增长、关联占用疑点
- 集团/实控人圈层：多主体、多层股权、多账户资金往来的穿透整理

## 何时使用

- “帮我把关联方边界梳理清楚，并判断关联交易是否合理”
- “怀疑关联交易虚增收入/利润转移/资金占用，想要核验清单”
- “需要为审查/贷后准备一份关联交易穿透备忘录”

## 何时不要使用

- 用户要求在缺少任何交易样本、合同、对账单的情况下做强定性结论
- 需要审计鉴证/司法认定才能确认的事项（本 skill 只给核验要点与条件化判断）
- 用户要求伪造合同、发票、流水或关联关系证明（明确拒绝）

## 默认工作流（建议按顺序输出）

1. **明确穿透目标**：本次是为了识别资金占用？还是识别利润转移？还是识别循环交易/虚增收入？（写清楚）
2. **界定关联方边界**：
   - 法定关联（股权/控制/一致行动/关键管理人员）
   - 实质关联（共同实控、同一资金池、同一办公/人员高度交叉、上下游壳公司）
3. **交易归类**：销售/采购、资金拆借、担保与或有、资产买卖、费用分摊、代收代付。
4. **合理性测试（把判断落到证据）**：
   - 价格/毛利：是否显著偏离外部可比
   - 账期/结算：是否“账期无限延长/对倒/期末突击”
   - 对手方能力：关联方是否具备经营能力与履约能力
5. **资金与货物流穿透**：识别回流、循环、同日往返、拆借与垫资。
6. **输出风险结论（条件化）**：列出红旗、核验要点、补件与下一步动作（含升级条件）。

## 重点分析框架（写作骨架）

- **边界**：关联方名单是否完整？是否存在“隐性关联”遗漏？
- **合理性**：交易是否有真实商业目的？定价与结算是否异常？
- **影响**：对收入、利润、现金流、负债与或有事项的影响是什么？
- **风险模式**：资金占用、利润转移、循环交易、虚增收入、掩盖债务、套取授信
- **缓释**：资金监管、回款归集、关联交易限额、加强反担保、退出/压降计划

## 输入要求

最小可用输入见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\references\input-schema.md)。

## 输出要求

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：运行 `t138` 场景，生成“关联交易穿透包”
- `..\shared\corporate_credit_skill_engine.py`：共享引擎（统一输出结构与规则）

## 参考资料与模板

- [related-party-boundary-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\references\related-party-boundary-guide.md)
- [related-transaction-penetration-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\references\related-transaction-penetration-checklist.md)
- [related-transaction-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\references\related-transaction-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\assets\example-input.json)
- [related-party-table-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\assets\templates\related-party-table-template.md)
- [penetration-memo-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\assets\templates\penetration-memo-template.md)
- [transaction-test-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t138-corporate-finance-task-assistant\assets\templates\transaction-test-template.md)

## 风险与边界

- 不把“关联/不关联”作为凭空定性：必须列核验点（股权、人员、地址、资金往来、业务实质）。
- 不把“疑似”写成“事实”：对每条红旗都标注依赖材料与待核验事项。
- 不输出伪造合同、发票、流水或监管口径。

## 信息不足时的处理

- 若只有关联方名单但缺交易样本：先输出“穿透目标 + 交易样本需求 + 最短补件路径 + 核验问题清单”。

