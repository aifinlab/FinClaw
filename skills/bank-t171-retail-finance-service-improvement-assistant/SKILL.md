---
name: bank-t171-retail-finance-service-improvement-assistant
description: "当用户需要在银行零售金融场景下，基于投诉、服务指标或体验反馈形成服务改进优先级与行动方案时使用本技能。适合输出问题排序、根因假设、改进动作和风险提示。"
---

# 服务改进建议助手

## 这个 skill 是做什么的
在零售金融服务场景中，把投诉与服务数据转成可执行的服务改进建议。输出包括问题优先级、可能根因、快速修复项、改进动作与风险提示，用于服务优化与运营复盘。

## 适用范围
- 零售客户经营、服务体验优化、投诉复盘、服务流程改造
- 客户经理、服务运营、体验管理与消保团队协同场景
- 服务问题清单、投诉VOC、NPS或时效指标的结构化分析

## 何时使用
- 需要明确服务问题优先级与改进动作时
- 需要把投诉与服务指标沉淀为可复盘的改进清单时

## 何时不要使用
- 缺少服务问题清单或时间窗口时
- 需要输出对外承诺、赔付结论或合规认定时

## 默认工作流
1. 明确服务改进目标与观察窗口
2. 汇总投诉、体验指标与问题清单
3. 计算问题优先级与影响范围
4. 给出根因假设、快速修复与改进动作
5. 标注风险事项与需复核环节

## 输入要求
- 批次与窗口：`batch_id`、`time_window`（建议包含 `start_date`/`end_date`）
- 服务问题清单：`service_issues[]`（建议字段 `issue_id`、`issue_name`、`complaint_count_30d`、`complaint_severity_avg`、`nps_delta`、`resolution_time_avg`、`affected_customers`、`process_stage`、`channel`、`compliance_risk`）
- 辅助信息（可选）：投诉VOC摘要、渠道服务指标、流程节点说明

## 输出要求
- 问题优先级清单（含影响与优先级）
- 根因假设与快速修复建议
- 改进动作清单与复盘要点
- 风险提示与需人工复核事项

## 风险与边界
- 不得输出对外赔付或违规认定结论
- 不得把假设写成事实，需标注为“需复核”
- 输出仅用于服务改进，不替代审批或合规结论

## 信息不足时的处理
- 先列出已掌握事实，再给出缺口清单
- 缺少关键字段时降级为“框架建议”
- 对依赖制度或人工核实的部分标注“待确认”

## 交付标准
- 能说明“重点问题、为什么、先做什么”
- 建议动作可执行，能进入服务改进清单
- 输出中清晰区分事实、假设与待确认事项

## 配套脚本
脚本入口：`scripts/run_skill.py`，调用 `shared/retail_service_skill_engine.py` 的 `t171` 场景。

```bash
python scripts/run_skill.py --input input.json --format markdown
python scripts/run_skill.py --input input.json --format json
```
