---
name: contract-clause-assistant
description: 用于合同条款结构化识别与完整性检查，自动识别关键条款类型并提示缺失项。适用于信托业务合同起草、条款体检、法务预审场景。
---

# 合同条款助手（T106）

## 概述

本技能用于对合同条款进行基础解析与完整性检查，重点覆盖：
- 付款与清偿条款
- 违约责任与救济机制
- 担保与追索条款
- 争议解决与适用法律

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `contract_name`
- `clause_no`
- `clause_title`
- `clause_text`

## 工作流

1. 导入合同条款清单
2. 运行脚本识别条款类别与覆盖情况
3. 检查缺失关键条款与模糊表述
4. 输出条款体检报告
5. 进入法务复核与修订

## 脚本调用指引

使用 `scripts/contract_clause_analysis.py` 生成报告：

```bash
python scripts/contract_clause_analysis.py \
  --input clauses.json \
  --output clause_report.md
```

可选参数：
- `--required`：自定义关键条款清单 JSON

## 输出结构

1. 条款覆盖总览
2. 条款分类结果
3. 缺失关键条款提示
4. 需人工复核条款
5. 方法与限制

## 质量要求

- 识别依据需可解释
- 缺失项必须明确列示
- 仅做条款层初筛，不替代律师审查意见
