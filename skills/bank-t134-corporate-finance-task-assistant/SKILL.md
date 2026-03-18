---
name: bank-t134-corporate-finance-task-assistant
description: "当用户需要在银行对公金融场景下，围绕财务快诊进行成因拆解、指标解读、问题归因或专题诊断时使用本技能。适合输出结构化诊断结论、驱动项说明、后续追问方向和业务提示。"
---

# 企业财报快诊助手

这个 skill 面向企业财报快诊场景，重点不是把财报再复述一遍，而是快速指出收入、利润、现金流、毛利、费用和周转指标里最值得追问的异常点。它适合在尽调、审查或客户拜访前，先做一轮“财务上最该问什么”的快诊。

## 适用范围
- 企业财报、管理报表和经营指标的快速诊断
- 尽调前、审查前、客户拜访前的财务问题梳理
- 需要输出成因拆解、追问方向和业务提示时
- 适用于客户经理、审查人员和业务中台的财务初筛场景

## 何时使用
- 用户说“帮我快速看这家企业财报哪里有问题”“先做财务快诊”时
- 用户已有近几期财报或管理报表，希望形成结构化诊断时
- 用户需要在短时间内识别最值得追问的财务异常点时

## 何时不要使用
- 只有口号式描述，没有任何财务数据或对比信息时
- 用户要求把快诊结果直接当成正式审计或最终授信结论时
- 需要会计准则专项判断但缺少基础报表时

## 默认工作流
1. 明确诊断对象、时间区间和比较口径。
2. 对收入、利润、现金流、毛利、费用和周转做快速扫描。
3. 找出最明显的背离项、异常项和结构变化。
4. 区分已知事实、可能解释和待补数据。
5. 输出快诊摘要、追问方向和后续动作。

## 重点分析框架
- 收入和利润：增长是否真实、质量是否稳定
- 现金流：利润是否顺利转化为现金
- 毛利和费用：结构变化来自价格、成本还是费用投放
- 周转与负债：应收、存货、债务压力是否同步恶化
- 追问方向：最值得补证据和追问的异常项

## 输入要求
- 企业名称和本次诊断目标
- 最近两到三期财报或管理报表
- 收入、利润、现金流、毛利、费用、应收、存货、债务等核心指标
- 历史对比口径、事件背景和管理层解释（如有）

详细字段见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\references\input-schema.md)。

## 输出要求
- 财报快诊摘要与初步建议
- 核心异常点和可能驱动项
- 资料缺口和补充数据建议
- 后续追问方向和业务提示

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：输出财报快诊包
- `shared/corporate_credit_skill_engine.py`：共享分析引擎，内含财务快诊专项规则

## 参考资料与模板

- [financial-quick-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\references\financial-quick-checklist.md)
- [cashflow-profit-guide.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\references\cashflow-profit-guide.md)
- [financial-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\references\financial-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\assets\example-input.json)
- [financial-diagnosis-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\assets\templates\financial-diagnosis-template.md)
- [question-list-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\assets\templates\question-list-template.md)
- [metric-compare-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t134-corporate-finance-task-assistant\assets\templates\metric-compare-template.md)

## 风险与边界
- 不得把财务快诊结果包装成正式审计、估值或审批结论。
- 不得编造财务数据、行业对比或管理层解释。
- 不得把相关性直接写成因果关系。
- 对推断较强的判断必须标注前提条件和数据局限。

## 信息不足时的处理
- 如果只有部分报表，先输出能确认的异常项和缺失数据清单。
- 如果历史对比口径不一致，优先提示口径问题，不强做趋势结论。
- 对无法确认的异常驱动项，明确列为待追问，不直接下判断。

## 交付标准
- 输出要让用户快速抓住最值得问的财务问题。
- 异常项应落到具体指标和可能成因，不停留在抽象判断。
- 至少回答“哪里异常、可能为什么、下一步问什么”三个问题。
