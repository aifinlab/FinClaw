---
name: contract-version-compare-assistant
description: 用于合同版本差异识别与风险变更追踪，比较新旧版本条款新增、删除、修改及风险关键词变化。适用于合同谈判轮次管理、法务复核和重大变更提示场景。
---

# 合同版本对比助手（T108）

## 概述

本技能用于对比合同新旧版本差异，重点识别：
- 新增或删除条款
- 关键措辞变化
- 风险条款强化或弱化

## 输入要求

支持 JSON 或 JSONL。推荐输入单个 JSON 对象，包含：

- `contract_name`
- `old_clauses`（条款数组）
- `new_clauses`（条款数组）

条款对象建议包含：
- `clause_no`
- `clause_title`
- `clause_text`

## 工作流

1. 准备新旧版本条款结构化文本
2. 运行脚本生成差异与风险变更报告
3. 复核高风险改动的业务影响
4. 输出法务复核意见与谈判建议
5. 归档版本迭代记录

## 脚本调用指引

使用 `scripts/contract_version_compare.py` 生成报告：

```bash
python scripts/contract_version_compare.py \
  --input version_pair.json \
  --output version_diff_report.md
```

可选参数：
- `--keywords`：自定义风险关键词 JSON
- `--top`：展示重点变化数量（默认 30）

## 输出结构

1. 版本差异概览（新增/删除/修改数量）
2. 重点变更条款清单
3. 风险变化提示（风险上升/下降）
4. 待复核条款
5. 方法与限制

## 质量要求

- 变化识别需可追溯到原文
- 风险变化必须给出关键词或规则依据
- 不替代律师审核结论
