---
name: bank-t187-wealth-management-redemption-retention-assistant
description: "Use when wealth-management teams need to respond to a redemption request by producing compliant retention talk tracks, options, and follow-up actions based on client goals, liquidity needs, and product facts. Trigger this skill for redemption-risk conversations, retention plans, and client-facing explanations that must avoid收益承诺 and明确风险边界。"
---

# 赎回挽留与沟通组织助手

本技能面向银行财富管理场景，围绕客户赎回请求或赎回风险信号，生成一套可执行的“挽留与沟通动作包”。目标是把客户画像、持仓事实、市场背景与合规边界组织成前台可直接使用的沟通主线、替代方案与后续跟进动作，同时清楚标注信息缺口与禁用表述。

## 适用范围
- 客户发起赎回申请或出现明显赎回意向
- 市场波动、业绩回撤或流动性冲击导致客户情绪不稳
- 产品持有期未满或存在赎回成本，需要合规解释
- 理财经理/私行顾问需要输出“沟通主线 + 方案选项 + 风险提示”

## 何时使用
- 需要在较短时间内输出“可直接使用”的挽留话术框架、沟通节奏与方案建议
- 需要把客户关切点、产品事实、市场解释和合规边界整合为统一口径
- 需要明确下一步跟进动作、复盘节点与留痕要点

## 何时不要使用
- 用户要求夸大收益、保证回本或规避适当性流程
- 未掌握关键事实却要求下结论或做“必留”承诺
- 需要正式投研结论或法律意见的场景

## 默认工作流
1. **确认事实与动因**：梳理客户赎回原因、现金流压力、持有期限、产品表现与风险等级匹配情况。
2. **识别缺口与约束**：标注缺失信息（期限、风险等级、产品条款、费用结构等）与合规边界。
3. **生成沟通主线**：先安抚情绪，再解释事实与边界，最后给出可选路径。
4. **产出挽留方案**：组合“部分赎回/分批赎回/转换/降波动配置/陪伴复盘”等选项。
5. **输出留痕清单**：明确需确认的客户要素、风险提示与下一步跟进动作。

## 输入要求
- 客户画像：风险偏好、投资目标、持有周期、流动性需求、沟通偏好
- 赎回请求：赎回金额/比例、紧急程度、主要原因、触达场景
- 持仓与产品信息：产品风险等级、期限、流动性、历史表现、费用/赎回成本
- 市场与事件：市场波动、政策/利率/行业事件、产品相关公告
- 合规约束：禁用表述、必须披露的风险点、渠道限制

## 输出要求
- 赎回动因与风险点摘要（含已确认与待核验信息）
- 统一口径的沟通主线（开场/事实/边界/方案/确认）
- 可选挽留方案与触发条件（部分赎回/分批赎回/转换/观望复盘）
- 合规提示与禁用表述清单
- 跟进动作与留痕要点（确认清单、复盘节点）

## 风险与边界
- 不得承诺收益或暗示“保本保收益”
- 不得绕过适当性审核或弱化风险提示
- 不得以不完整事实输出确定性结论
- 所有判断必须区分“已确认事实 / 待核验信息 / 合理推测”

## 信息不足时的处理
- 明确列出信息缺口，并在输出中标注“待补充/待确认”
- 先输出沟通框架与可选路径，避免给出绝对结论
- 对外部数据或制度口径需注明依赖来源

## 交付标准
- 输出能被一线直接使用：一句话主线 + 可选方案 + 风险提示
- 明确“为什么这样说、为什么这样做、下一步怎么走”
- 沟通内容可留痕、可复核、合规可解释

## 使用的脚本与资料
- `scripts/wealth_redemption_retention.py`：根据输入生成挽留动作包（Markdown/JSON）
- `scripts/run_skill.py`：命令行入口
- `references/input-schema.md`：输入字段口径
- `references/output-schema.md`：输出结构口径
- `references/redemption-checklist.md`：赎回核验清单
- `references/retention-strategy-framework.md`：挽留方案框架
- `references/compliance-red-lines.md`：合规禁用表述
- `references/conversation-flow.md`：沟通节奏模板
- `assets/templates/retention-plan-template.md`：挽留方案模板
- `assets/templates/call-script-template.md`：电话/面谈话术模板
- `assets/templates/risk-disclosure-template.md`：风险提示模板
- `assets/templates/follow-up-tasklist.md`：跟进任务清单模板
- `assets/example-input.json`：示例输入
