---
name: bank-t170-retail-finance-work-order-classification-assistant
description: "当用户需要在银行零售金融场景下，对客户工单进行分类归因、优先级排序与路由建议时使用本技能。适合输出分类分布、优先级清单与SLA风险提示。"
---

# 工单分类助手

本技能用于把零散的服务工单归类为可管理的类别与优先级，生成路由建议与复盘清单。强调分类口径一致、责任归口清晰、SLA风险可见。

## 适用范围
- 客服/运营工单分类与路由
- 服务质量周报/月报
- SLA风险识别与优先级管理

## 何时使用
- 工单量大、需要快速分类与排序时
- 需要统一口径和责任归口时

## 何时不要使用
- 没有工单样本或时间窗口时
- 需要正式审计或合规认定的场景

## 默认工作流
1. 明确工单口径与统计窗口
2. 分类（类型/产品/渠道/环节）并生成分布
3. 识别高优先级工单并给出路由建议
4. 输出SLA风险与复盘建议

## 重点分析框架
- 分类口径是否清晰、可复用
- 高优先工单是否及时识别
- 路由建议是否匹配责任团队
- SLA风险是否可追溯

## 输入要求
- 最低可用输入：`time_window`、`work_orders`
- 推荐输入字段见 `references/input-schema.md`

## 输出要求
- 分类分布与TOP问题
- 高优先级工单清单
- 路由建议与责任归口
- SLA风险提示与复盘动作

## 风险与边界
- 不输出“定责/处罚”结论
- 分类结果需标注依据与待核验项

## 信息不足时的处理
- 输出保守分类与缺口清单
- 提示需补充工单字段或标签

## 交付标准
- 分类结果可直接用于运营管理
- 输出可追溯、可复盘

## 配套脚本

```bash
python scripts/run_skill.py --input assets/example-input.json --format markdown
python scripts/run_skill.py --input assets/example-input.json --format json
```

脚本入口：`scripts/run_skill.py`（调用 `shared/retail_service_ops_skill_engine.py` 的 `t170` 场景）。
