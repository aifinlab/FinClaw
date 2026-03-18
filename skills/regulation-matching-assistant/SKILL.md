---
name: regulation-matching-assistant
description: 用于法规要求与业务条款匹配检查，基于监管规则关键词识别已覆盖义务与潜在缺口。适用于合同法务、合规审查、监管检查前自查场景。
---

# 法规匹配助手（T109）

## 概述

本技能用于将业务文本或合同条款与法规要求进行匹配，输出：
- 已覆盖监管要求
- 未覆盖或覆盖不足项
- 需补充条款建议

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `item_id`
- `scenario`
- `jurisdiction`
- `clause_text`
- `asset_type`

## 工作流

1. 明确适用法域与监管口径
2. 导入待匹配条款文本
3. 运行脚本完成法规匹配与缺口识别
4. 复核缺口项并形成补充建议
5. 输出合规匹配报告

## 脚本调用指引

使用 `scripts/regulation_matcher.py` 生成报告：

```bash
python scripts/regulation_matcher.py \
  --input clauses.json \
  --output regulation_match_report.md
```

可选参数：
- `--rules`：自定义法规规则 JSON
- `--top`：展示重点缺口数量（默认 20）

## 输出结构

1. 匹配结果概览
2. 法规覆盖矩阵
3. 重点缺口与风险提示
4. 补充条款建议
5. 方法与限制

## 质量要求

- 匹配关系可追溯到关键词/规则
- 缺口提示要具体到义务点
- 仅提供合规辅助判断，不构成法律意见
