---
name: bank-t176-wealth-management-product-suitability-rm-assistant
description: "Use when a relationship manager needs to match wealth-management products to a client profile, compare main and backup options, and produce compliant suitability notes, communication points, and follow-up actions."
---

# 理财产品适配助手（理财经理版）

这个 skill 面向银行财富管理一线理财经理，核心是把客户画像、风险承受能力、期限与流动性约束、当前持仓与产品池做出清晰的适当性匹配，并生成可直接用于客户沟通的适配结论与合规提示。

## 适用范围
- 理财产品适配、可售产品筛选、主备选方案比较
- 客户风险匹配校验、适当性记录、合规解释话术
- 适合理财经理在客户面谈前形成清晰的推荐逻辑与风险提示

## 何时使用
- 需要在产品池中筛出适配产品并形成主/备方案时
- 需要输出“为什么推荐/为什么不推荐”的可解释结论时
- 需要同步产出风险提示、信息缺口与后续跟进动作时

## 何时不要使用
- 客户风险等级、期限或流动性约束未确认就要求直接给出强推荐
- 用户要求规避适当性、合规披露或承诺收益

## 默认工作流
1. 汇总客户画像与核心约束：风险等级、期限、流动性、目标用途
2. 拉取产品池与关键信息：风险等级、期限、流动性、资产类别
3. 进行适配筛选：风险/期限/流动性硬约束优先
4. 输出主方案与备选方案，标注不适配产品与原因
5. 给出风险披露话术、客户沟通提纲与下一步跟进清单

## 重点分析框架
- 适当性：产品风险等级 ≤ 客户风险等级
- 期限匹配：产品最低持有期 ≤ 客户可接受期限
- 流动性匹配：产品流动性 ≥ 客户流动性需求
- 目标匹配：收益/稳健/流动性目标与产品标签一致
- 证据链：适配结论可追溯到客户信息与产品要素

## 输入要求
- 客户画像：风险等级、投资期限、流动性需求、目标用途
- 现有持仓（如需诊断）：资产类别、金额、期限、流动性
- 产品池：产品名称、风险等级、期限、流动性、资产类别、标签
- 其他约束：禁投品类、偏好资产类别、监管或渠道限制

## 输出要求
- 适配产品清单与评分说明
- 不适配产品及原因
- 主方案与备选方案（含适配逻辑）
- 风险提示、沟通要点与后续行动

## 代码与文件
- `scripts/run_skill.py`：运行适配评估并输出 Markdown/JSON
- 共享引擎：`shared/wealth_management_skill_engine.py`

示例命令：

```bash
python scripts/run_skill.py --input assets/example-input.json --format markdown
```

## 参考资料
- `references/input-schema.md`
- `references/output-schema.md`
- `references/suitability-checklist.md`
- `references/client-interview-outline.md`
- `references/risk-disclosure-points.md`

## 风险与边界
- 不得承诺收益或回本
- 不得在缺少关键字段时输出确定性结论
- 不得把适配建议包装成审批结论
- 需清晰区分已确认信息与待核验信息

## 信息不足时的处理
- 明确列出缺失信息与优先补充项
- 输出可用的适配框架与待确认事项，不凭空补全
- 依赖外部材料的内容必须标注“待确认/待补充”

## 交付标准
- 输出可被理财经理直接用于客户沟通
- 适配逻辑可解释、可追溯、可复核
- 风险提示、合规边界与下一步动作齐全
