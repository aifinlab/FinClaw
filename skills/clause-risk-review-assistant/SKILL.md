---
name: clause-risk-review-assistant
description: 用于合同条款风险审查，基于关键词与规则识别高风险表述（单方决定、责任失衡、模糊期限、无限责任等）并输出修订建议。适用于法务风控预审、合同谈判前风险筛查场景。
---

# 条款风险审查助手（T107）

## 概述

本技能用于识别合同条款中的常见风险表达，输出风险等级与修订建议，辅助法务快速聚焦重点条款。

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `contract_name`
- `clause_no`
- `clause_title`
- `clause_text`

## 工作流

1. 汇总待审查条款
2. 运行脚本进行风险扫描
3. 对高风险条款补充法律判断
4. 输出风险清单与修订建议
5. 跟踪修订闭环

## 脚本调用指引

使用 `scripts/clause_risk_review.py` 生成报告：

```bash
python scripts/clause_risk_review.py \
  --input clauses.json \
  --output clause_risk_report.md
```

可选参数：
- `--rules`：自定义风险规则 JSON
- `--top`：展示高风险条款数量（默认 20）

## 输出结构

1. 风险等级统计
2. 高风险条款清单
3. 风险命中依据与建议修改方向
4. 待律师复核事项
5. 方法与限制

## 质量要求

- 每个风险命中必须给出触发依据
- 修订建议需具体可执行
- 不输出法律结论，仅输出审查建议
