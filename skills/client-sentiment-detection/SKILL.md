---
name: client-sentiment-detection
description: 面向基金投顾与客户服务领域的情绪识别任务Skill，围绕「客户情绪识别助手」场景提供信息抽取、结构化分析与结果输出。
---

# 客户情绪识别助手 Skill

## 数据来源

### 1. 输入类型

- 基金公告/定期报告/招募说明书/产品说明材料
- 净值与收益时间序列、持仓与资产配置披露
- 销售/服务记录、客户反馈与问答素材(如适用)
- 合规口径与品牌内容规范(如适用)

### 2. 主要数据要素

- 客户持仓结构与收益区间
- 风险偏好、适当性与行为标签
- 近期市场与产品动态
- 常见问题与服务记录
- 监管适当性要求与服务规范

### 3. 质量要求

- 输入信息尽量完整，包含时间区间、基金代码与核心指标
- 若来自 OCR/截图，请尽量校对错字与断行
- 对于未披露的数据需明确标注“缺失/待补充”

---

## 核心能力

- 提取核心指标(收益、风险、风格、持仓特征)并进行结构化汇总
- 识别优势/短板与关键驱动因子，形成可追溯的分析链条
- 对异常波动或结构变化给出原因假设与影响评估
- 输出可执行的跟进建议与观察清单
- 输出触达/陪伴策略与关键沟通节奏
- 沉淀客户异议与情绪标签，形成安抚与引导话术

---

## 输出结构

### 1. 基础字段

- skill
- domain
- scene
- input_summary
- key_findings
- data_quality
- limitations

### 2. 场景扩展模块(按需输出)

- analysis
- metrics
- diagnosis
- risks
- recommendations
- customer_strategy
- segments
- touchpoints
- tone

---

## 使用示例

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行脚本

```bash
python scripts/main.py --input sample.txt --output-json result.json --output-md report.md
```

### 3. 输出示例

```json
{
  "skill": "客户情绪识别助手",
  "domain": "投顾与客户服务",
  "scene": "情绪识别",
  "input_summary": {
    "fund_code": "000000",
    "fund_name": "示例基金",
    "period": "2024Q4",
    "data_coverage": "净值/持仓/披露/市场"
  },
  "key_findings": [
    "关键结论1",
    "关键结论2"
  ],
  "data_quality": {
    "has_text": true,
    "text_length": 1200
  },
  "limitations": [
    "仅基于输入信息形成初步判断"
  ]
}
```

---

## 注意事项与限制

- 仅对输入文本进行结构化与初步判断，不替代人工投研或合规结论
- 若缺少关键数据(持仓、基准、时间区间)，结果需明确提示不完整
- 输出建议应结合实际业务口径与监管要求复核

---

## 适用场景

- 业务条线: 投顾与客户服务
- 场景/能力: 情绪识别
- 典型用户: 研究员、产品经理、渠道与客服、合规审查或内容运营人员

---

## License

- 代码部分遵循 MIT License
- 数据来源与披露口径需遵循对应数据供应商与监管要求
