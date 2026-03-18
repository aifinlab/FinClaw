---
name: bank-t177-wealth-management-product-suitability-private-banking-assistant
description: "Use when a private-banking advisor needs to match products to a high-net-worth or family-wealth profile, compare main and backup options, and produce suitability logic, family-balance notes, and compliant communication points."
---

# 理财产品适配助手（私行顾问版）

这个 skill 面向私行顾问场景，强调家庭资产视角、复杂约束与多目标平衡。在完成适当性匹配的同时，输出家庭资产结构影响、税务/合规注意点与可执行沟通提纲。

## 适用范围
- 私行客户产品适配、方案比较、家庭资产结构优化
- 复杂需求下的适配逻辑说明与风险揭示
- 适合输出“主方案 + 备选方案 + 家庭平衡建议”的全链路材料

## 何时使用
- 高净值/家族客户需要组合式产品适配与适当性判断时
- 需要输出家庭资产结构、现金流安排与跨周期配置建议时
- 需要形成可复核的适配记录与沟通话术时

## 何时不要使用
- 家庭资产结构、风险等级或核心约束未确认就要求强推方案
- 用户要求规避适当性、税务合规披露或收益承诺

## 默认工作流
1. 明确客户/家庭核心目标、风险等级与关键约束
2. 建立家庭资产结构与现金流安排概览
3. 对产品池做适配筛选（风险、期限、流动性优先）
4. 输出主备方案，并说明对家庭资产结构的影响
5. 给出风险披露、税务/合规提示与后续动作清单

## 重点分析框架
- 家庭资产视角下的风险暴露与集中度
- 适当性与期限匹配：不以高收益覆盖风险错配
- 现金流与流动性安排：长期配置与短期用款分层
- 跨周期与跨币种一致性：口径要清晰、可披露

## 输入要求
- 客户风险等级、目标、期限、流动性需求
- 家庭资产结构概览（现金流、核心资产、长期配置）
- 产品池信息：风险等级、期限、流动性、资产类别、标签
- 税务/合规或家族治理相关约束（如适用）

## 输出要求
- 适配产品清单与适配逻辑
- 主方案与备选方案，并说明对家庭资产结构的影响
- 不适配产品及原因
- 风险披露与沟通要点
- 后续补充材料与跟进动作

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
- 不得以适配建议替代审批/合规结论
- 涉及税务、跨境与家族治理内容需标注“待核验”
- 适配结论仅基于已披露信息

## 信息不足时的处理
- 先输出已确认部分与缺口清单
- 对关键口径差异（税务、跨币种、家族治理）明确待核验项
- 不得以推测替代事实

## 交付标准
- 输出可直接用于私行沟通与复核
- 家庭资产结构影响与风险提示清晰可追溯
- 逻辑一致、可复核、可解释
