---
name: financing-entity-dd-gov-assistant
description: 用于政信项目中的融资主体尽调，支持财政实力、债务负担、偿债能力、政策支持与风险事件的结构化评估。适用于信托项目立项前主体筛查、尽调底稿整理与风控复核，采用多脚本流程（JS 预处理 + Python 评分报告）并可加载配置与参考基线数据。
---

# 融资主体尽调助手-政信版（T771）

## 概述

本技能面向政信类融资主体尽调场景，提供“数据标准化 + 规则评分 + 报告输出”的完整链路，重点覆盖：
- 财政实力与债务负担（债务收入比、财政支出压力）
- 偿债与流动性（DSCR、现金短债覆盖）
- 政策支持与风险事件信号
- 数据完整性与复核优先级

## 输入要求

支持 JSON 数组或 JSONL，单条记录建议包含字段：
- 基础信息：`entity_name`, `region`, `as_of_date`
- 财政与债务：`revenue`, `fiscal_expenditure`, `general_debt_balance`, `hidden_debt_est`, `interest_bearing_debt`
- 偿债能力：`debt_service_coverage`, `cash_reserve`, `short_term_debt`, `revenue_growth`, `self_sufficiency_ratio`
- 事件与政策文本：`policy_support_text`, `event_text`, `fiscal_status_text`

## 工作流程

1. 收集主体数据并统一字段口径
2. 使用 JS 脚本进行数据清洗与衍生指标计算
3. 使用 Python 脚本加载评分规则与基线数据进行评估
4. 生成结构化 Markdown 尽调报告
5. 人工复核高风险主体并补充尽调结论

## 执行方式

按顺序执行以下脚本：

1. 数据预处理（Node.js）：
```bash
node scripts/gov_dd_preprocess.js \
  --input raw_entities.jsonl \
  --output processed_entities.json
```

2. 规则评分与报告输出（Python）：
```bash
python scripts/gov_dd_scoring.py \
  --input processed_entities.json \
  --rules config/scoring_rules.json \
  --baseline reference/gov_credit_baseline.json \
  --output gov_dd_report.md
```

中间产物：
- `processed_entities.json`（标准化 JSON 数组）
- 字段包含原始值、衍生比率、完整度得分，供评分脚本直接消费

## 输出结构

1. 样本概览（数量、平均分、风险等级分布）
2. 主体评分排序（主体、区域、评分、等级）
3. 重点风险明细（事实字段、规则命中、复核建议）
4. 方法与口径说明（规则来源、基线参数）
5. 免责声明（自动生成需人工复核）

## 质量要求

- 事实与判断分离，规则命中须可追溯
- 评分逻辑必须由 `config/scoring_rules.json` 显式定义
- 报告必须包含自动生成与人工复核免责声明
- 不输出投资、授信或法律最终结论
