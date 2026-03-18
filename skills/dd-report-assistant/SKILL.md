---
name: dd-report-assistant
description: 用于尽调报告结构化生成与风险摘要整理，基于尽调发现自动输出执行摘要、风险分布、关键问题与后续动作清单。适用于信托项目尽调底稿整理、会审材料准备和阶段性汇报场景。
---

# 尽调报告助手（T105）

## 概述

本技能用于将尽调发现快速整合成标准化报告，支持：
- 风险分级统计
- 分类问题归纳
- 重点风险与行动项生成

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `project_name`
- `entity_name`
- `category`（finance/legal/compliance/operations）
- `finding`
- `severity`（critical/high/medium/low）
- `evidence`
- `recommendation`
- `status`

## 工作流

1. 汇总尽调发现并规范字段
2. 运行脚本生成结构化报告草稿
3. 复核关键事实与证据引用
4. 补充人工判断与结论边界
5. 输出正式尽调报告

## 脚本调用指引

使用 `scripts/dd_report_builder.py` 生成报告：

```bash
python scripts/dd_report_builder.py \
  --input findings.json \
  --output dd_report.md
```

可选参数：
- `--top`：展示重点风险数量（默认 15）

## 输出结构

1. 执行摘要
2. 风险分布统计
3. 分类发现与重点风险
4. 待办行动项
5. 方法与限制声明

## 质量要求

- 风险结论必须可追溯到发现与证据
- 事实与建议分离
- 明确未覆盖事项
- 不输出投资建议，仅输出尽调意见草稿
