# 输出结构说明（产品卖点包）

## 顶层字段

- `summary`：一句话结论
- `profile_snapshot`：客户画像摘要
- `selling_points`：卖点清单（含证据、适配与合规提示）
- `suitability_result`：适配结论与缺口
- `risk_disclosures`：风险提示/披露要点
- `objection_handling`：常见异议与回应
- `talking_points`：沟通要点话术
- `comparison_options`：备选方案与不建议方案
- `follow_up_actions`：跟进动作
- `pending_confirmations`：待客户确认清单

## selling_points

数组结构，每条包含：

- `point`：卖点表述
- `evidence`：证据或条款来源
- `suitable_for`：适配人群或场景
- `boundary`：边界或限制

## suitability_result

- `status`：适配/谨慎/不适配
- `rationale`：适配理由
- `gaps`：信息缺口（数组）

## objection_handling

数组结构，每条包含：

- `objection`：异议点
- `response`：建议回应
- `risk_note`：风险提示（可选）

## comparison_options

- `primary`：主方案摘要
- `alternatives`：备选方案列表
- `not_recommended`：不建议方案列表

## follow_up_actions

- 补齐材料/确认风险等级
- 复访节奏/说明材料发送
- 记录合规留痕事项
