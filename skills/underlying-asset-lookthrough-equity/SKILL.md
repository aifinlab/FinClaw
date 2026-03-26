---
name: underlying-asset-lookthrough-equity
description: 用于信托领域项目尽调中的底层资产穿透助手-股权版场景。支持结构化输入处理、规则分析与Markdown结果输出。
---

# 底层资产穿透助手-股权版（T784）

## 概述

本技能面向“项目尽调 / 资产穿透”业务单元，输出结构化分析报告与风险提示，支持尽调、法务、风控及存续管理流程中的基础判断。

## 输入要求

- 支持 JSON 数组或 JSONL
- 单条记录建议包含：`id`, `name`, `text`, `status`, `timestamp` 及相关业务字段
- 复杂版本可接入外部行业指标字段并通过规则文件扩展

## 工作流程

1. 明确分析口径与时间范围
2. 读取并清洗输入数据
3. 运行规则匹配与评分
4. 输出结构化报告并标注复核项
5. 人工复核后进入业务决策环节

## 执行方式

按顺序执行：

1. 预处理（Node.js）
```bash
node scripts/t784_preprocess.js --input input.jsonl --output processed.json
```

2. 分析与报告（Python）
```bash
python scripts/t784_analysis.py --input processed.json --rules config/rules.json --baseline reference/baseline.json --output report.md
```

## 输出结构

1. 样本概览（数量、分布）
2. 重点条目（评分、等级、触发原因）
3. 风险提示与复核建议
4. 免责声明

## 质量要求

- 事实与判断分离，规则命中可追溯
- 明确数据缺口与假设边界
- 所有输出结论必须保留人工复核提示
- 不输出投资建议、授信结论或法律最终意见

## 使用示例

### 示例 1: 基本使用

```python
# 调用 skill
result = run_skill({
    "param1": "value1",
    "param2": "value2"
})
```

### 示例 2: 命令行使用

```bash
python scripts/run_skill.py --input data.json
```
