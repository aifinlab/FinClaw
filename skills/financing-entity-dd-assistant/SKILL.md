---
name: financing-entity-dd-assistant
description: 用于融资主体尽调的结构化风险扫描与初判，覆盖财务数据核对、工商信息排查、涉诉执行风险识别、负面舆情关键词扫描。适用于信托/资管项目立项前的主体初筛、尽调底稿整理、投前风控复核等场景。
---

# 融资主体尽调助手（T101）

## 概述

本技能面向信托与资管业务中的融资主体尽调场景，帮助快速完成以下基础动作：
- 核对财务口径一致性与偿债能力信号
- 排查工商状态、行政处罚、经营异常等合规风险
- 扫描涉诉、被执行、失信等司法风险
- 聚合负面舆情关键词，输出可复核的风险摘要

该技能输出的是规则化初判结果，不替代律师、审计或投委会最终判断。

## 输入要求

建议输入 JSON 数组或 JSONL，每条记录对应一个融资主体。字段可按需裁剪，常用字段如下：

- 主体基础信息：
  - `entity_name`
  - `industry`
  - `as_of_date`
- 财务核对相关：
  - `reported_revenue`（管理口径营收）
  - `tax_revenue`（税务口径营收）
  - `debt_asset_ratio`
  - `net_profit_margin`
  - `net_profit`
  - `operating_cashflow`
  - `current_ratio`
- 工商与合规相关：
  - `business_status_text`
  - `abnormal_operation_count`
  - `admin_penalty_count`
  - `share_pledge_ratio`
- 司法风险相关：
  - `litigation_count`
  - `dishonest_executed_count`
  - `executed_amount`
  - `litigation_text`
- 舆情相关：
  - `news`（字符串数组或对象数组）
  - `public_opinion_text`

## 工作流

1. 明确尽调对象、统计时点与口径（合并口径/母公司口径/单体口径）
2. 采集并清洗主体数据（财务、工商、司法、舆情）
3. 运行脚本生成主体风险评分与分维度结论
4. 对高分主体逐条复核命中项与证据来源
5. 输出《主体尽调风险初判报告》并形成待补证清单

## 脚本调用指引

使用 `scripts/entity_dd_analysis.py` 生成 Markdown 报告：

```bash
python scripts/entity_dd_analysis.py \
  --input input.json \
  --output entity_dd_report.md
```

可选参数：
- `--keywords`：自定义关键词规则 JSON 文件（覆盖默认舆情/涉诉关键词）
- `--top`：报告中展示的高风险主体数量（默认 10）

## 输出结构

1. 报告总览（样本数、风险等级分布、均分）
2. 主体风险排名（分数、等级、核心命中项）
3. 主体分维度结论：
   - 财务数据核对
   - 工商合规排查
   - 涉诉执行扫描
   - 舆情关键词扫描
4. 数据缺口与待补充资料清单
5. 方法说明与限制声明

## 质量要求

- 每条风险结论必须对应规则命中证据
- 明确“事实/规则命中”与“人工判断建议”的边界
- 对缺失字段单独列示，不得隐性忽略
- 不输出投资建议或授信结论，仅输出尽调初判与复核建议
