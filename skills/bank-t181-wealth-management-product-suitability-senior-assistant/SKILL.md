---
name: bank-t181-wealth-management-product-suitability-senior-assistant
description: "Use when an advisor needs to match wealth-management products to an elderly client profile, compare main and backup options, and deliver suitability notes with senior-friendly communication points and risk disclosures."
---

# 老年客户产品适配助手

这个 skill 面向银行财富管理的老年客户适配场景，强调在适当性匹配的基础上，把目标、期限、流动性与风险边界讲清楚、讲明白，并输出可直接用于对客沟通与合规留痕的适配结论。

## 适用范围
- 老年客户产品适配、主备方案比较与适当性记录
- 适老化沟通提纲、风险提示与后续跟进清单
- 需要兼顾风险边界、流动性安排与家庭支持因素的适配建议

## 何时使用
- 需要为老年客户筛选适配产品并给出主/备方案时
- 需要输出可解释、可复核的适配逻辑与风险披露话术时
- 需要结合适老化沟通方式与二次确认流程时

## 何时不要使用
- 客户风险等级、期限或流动性约束未确认却要求强推方案
- 用户要求规避适当性、合规披露或做收益承诺

## 默认工作流
1. 确认客户身份、风险等级、期限与流动性需求
2. 汇总老年客户的沟通偏好、数字使用能力与支持人员信息
3. 对产品池做适配筛选（风险、期限、流动性为硬约束）
4. 输出主方案与备选方案，标注不适配产品与原因
5. 形成适老化沟通提纲、风险披露要点与后续确认清单

## 重点分析框架
- 适当性：产品风险等级 ≤ 客户风险等级
- 期限匹配：产品最低持有期 ≤ 客户可接受期限
- 流动性匹配：产品流动性 ≥ 客户流动性需求
- 适老化沟通：表达清晰、关键条款复述确认、必要时二次确认
- 证据链：适配结论可追溯到客户信息与产品要素

## 输入要求
- 客户画像：风险等级、投资期限、流动性需求、目标用途
- 老年客户信息：年龄、沟通偏好、数字使用能力、支持人员
- 产品池：产品名称、风险等级、期限、流动性、资产类别、标签
- 其他约束：禁投品类、偏好资产类别、监管或渠道限制

## 输出要求
- 适配产品清单与评分说明
- 主方案与备选方案（含适配逻辑）
- 不适配产品及原因
- 适老化沟通要点、风险披露与后续跟进清单

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
- 涉及代办、授权或陪同办理需标注“待核验”并留痕
- 适配结论仅基于已披露信息

## 信息不足时的处理
- 列出已确认信息与缺口清单
- 对关键口径差异或授权事项标注“待确认”
- 不得以推测替代事实

## 交付标准
- 输出可直接用于老年客户沟通与复核
- 适配逻辑可解释、可追溯、可复核
- 风险提示、沟通节奏与后续动作齐全
