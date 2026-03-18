---
name: bank-t137-corporate-finance-task-assistant
description: "当用户需要在银行对公场景下对企业担保链条做风险扫描（传导路径、代偿触发点、圈层暴露、升级条件），并输出核验要点、补件清单、处置建议与升级路径时触发本技能。适合尽调/审查/贷后预警的结构化扫描。"
---

# 企业担保链风险扫描助手

担保链风险的难点不在“有没有担保”，而在“担保如何传导、何时触发、触发后谁会被拖下水”。这个 skill 用于把分散的担保信息，整理成一份可以直接用于尽调、审查与贷后监测的扫描包：

- 担保链条摘要（谁给谁担保，担保类型与金额，是否互保/循环担保）
- 传导路径（关键节点、强关联圈层、单点故障）
- 代偿触发点（被担保方经营/融资/诉讼触发，交叉违约）
- 升级条件与处置动作（需要现场核验的、需要风控升级的、需要压降/重组的）

## 适用范围

- 授信尽调/审查：识别担保链对现金流、负债与或有风险的影响，设置条件
- 贷后预警：担保圈层出现事件（被担保方逾期/诉讼/抽贷）时快速判断传导
- 风险排查：互保圈、区域担保圈、产业链担保圈的专项扫描

## 何时使用

- “这家企业对外担保多，帮我扫一遍担保链风险与传导路径”
- “出现代偿/诉讼/抽贷新闻，想判断是否会传导到我行敞口”
- “互保圈客户，想做贷后监测口径与升级条件”

## 何时不要使用

- 用户希望仅凭“担保圈传言”下违规定性结论（应转为核验清单与证据链）
- 需要法律意见才能确认担保效力的事项（本 skill 只给核验要点，不给法律结论）
- 用户要求伪造担保合同/反担保材料（明确拒绝）

## 默认工作流（建议按顺序输出）

1. **先定扫描口径**：时间窗口、担保类型（保证/抵押/质押/票据/保函/承诺函）、合并口径。
2. **把链条写成“可读摘要”**：核心节点、互保关系、循环担保、关键担保人。
3. **识别传导路径与单点故障**：
   - 被担保方出险会先冲击谁（代偿义务、交叉违约、资金冻结）
   - 哪个节点一倒会带来连锁反应（关键担保人/共同股东/同一资金池）
4. **列核验要点与补件**：担保合同要素、反担保、担保余额、保证期间、是否存在重复担保/超授权。
5. **给出处置与升级条件**：监测阈值、预警指标、升级到风控/法务的条件。

## 重点分析框架（写作骨架）

- **担保规模**：对外担保余额/净资产比例/集中度
- **链条结构**：互保/循环担保/多层嵌套/跨行业跨区域
- **触发机制**：代偿触发点、交叉违约、担保效力与授权
- **暴露测算**：最坏情景下的代偿敞口与现金流压力（只做条件化提示）
- **处置路径**：压降、置换、追加反担保、资金监管、名单管理

## 输入要求

最小可用输入见 [input-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\references\input-schema.md)。

## 输出要求

建议输出结构见 [output-schema.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\references\output-schema.md)。

## 配套脚本

- `scripts/run_skill.py`：运行 `t137` 场景，生成“担保链风险扫描包”
- `..\shared\corporate_credit_skill_engine.py`：共享引擎（统一输出结构与规则）

## 参考资料与模板

- [guarantee-chain-scan-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\references\guarantee-chain-scan-checklist.md)
- [guarantee-evidence-checklist.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\references\guarantee-evidence-checklist.md)
- [guarantee-chain-red-flags.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\references\guarantee-chain-red-flags.md)
- [example-input.json](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\assets\example-input.json)
- [guarantee-chain-scan-memo-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\assets\templates\guarantee-chain-scan-memo-template.md)
- [guarantee-chain-map-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\assets\templates\guarantee-chain-map-template.md)
- [escalation-note-template.md](C:\Users\zlf13\claude-program\finclaw-workspace\skills-jiaofu\bank-add\bank-t137-corporate-finance-task-assistant\assets\templates\escalation-note-template.md)

## 风险与边界

- 不把扫描结果当作法律结论或最终处置结论；对“担保效力”仅列核验要点。
- 不夸大传播链条风险；对“传导假设”必须标注前提与待核验事项。
- 对涉及外部负面事件的内容，必须标注时间窗口与信息来源摘要（如用户提供）。

## 信息不足时的处理

- 缺少担保合同/反担保/余额明细时，优先输出“补件清单 + 核验要点 + 升级条件”，避免强结论。

