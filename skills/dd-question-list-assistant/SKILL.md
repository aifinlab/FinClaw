---
name: dd-question-list-assistant
description: 用于尽调问题清单自动生成与优先级排序，基于尽调发现、缺失资料和风险关键词生成可执行的访谈问题与补证清单。适用于信托项目尽调访谈准备、问题台账整理、尽调会前复核场景。
---

# 尽调问题清单助手（T103）

## 概述

本技能用于把零散尽调发现转化为结构化问题清单，支持：
- 自动提炼高优先级访谈问题
- 关联证据与缺失材料，形成可执行补证项
- 输出会前问题台账，辅助尽调沟通

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `entity_name`
- `category`（finance/legal/compliance/operations/other）
- `issue_text`
- `severity`（high/medium/low）
- `evidence`
- `missing_docs`（字符串数组）
- `status`（open/closed/in_progress）

## 工作流

1. 汇总尽调初筛发现与证据
2. 运行脚本进行问题抽取与优先级打分
3. 复核高优先问题并补充业务化表述
4. 输出访谈问题清单与资料补充清单
5. 跟踪问题状态并闭环

## 脚本调用指引

使用 `scripts/dd_question_list.py` 生成报告：

```bash
python scripts/dd_question_list.py \
  --input findings.json \
  --output dd_questions.md
```

可选参数：
- `--keywords`：自定义关键词与问题模板 JSON
- `--top`：展示最高优先级问题数量（默认 20）

## 输出结构

1. 问题清单概览（总数、优先级分布）
2. 高优先问题列表（问题、依据、建议核验动作）
3. 分类问题池（财务/法务/合规/运营）
4. 补充资料清单
5. 方法说明与限制

## 质量要求

- 每个问题必须绑定发现依据
- 优先级规则需可复核
- 缺失资料单独汇总
- 不输出授信/投资结论，仅输出尽调问题建议
