---
name: legal-qa-assistant
description: 用于法务问答分流与标准化答复草案生成，基于问题关键词识别主题、紧急程度和建议处理路径。适用于信托业务法务咨询台账、问题分派与初步答复场景。
---

# 法务问答助手（T110）

## 概述

本技能用于对法务问答进行快速归类与优先级分流，输出标准化答复草案与升级处理建议。

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `question_id`
- `question`
- `context`
- `asker_role`
- `deadline_text`

## 工作流

1. 汇总法务问题文本
2. 运行脚本完成主题识别与紧急度评估
3. 生成答复草案与处理建议
4. 对高风险问题升级律师复核
5. 输出问答台账报告

## 脚本调用指引

使用 `scripts/legal_qa_triage.py` 生成报告：

```bash
python scripts/legal_qa_triage.py \
  --input legal_questions.json \
  --output legal_qa_report.md
```

可选参数：
- `--kb`：自定义问答规则与答复模板 JSON
- `--top`：展示最高优先级问题数量（默认 20）

## 输出结构

1. 问题总览与紧急度分布
2. 高优先问题清单
3. 主题分类结果与答复草案
4. 升级处理建议
5. 方法与限制

## 质量要求

- 分类和优先级要有明确依据
- 答复草案需保留合规边界声明
- 不输出最终法律意见，需律师终审
