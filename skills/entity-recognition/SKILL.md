---
name: entity-recognition
description: 用于金融文本中实体识别的原子技能，包括公司主体、金融产品、监管机构、关键人物等实体类型的识别和抽取。适用于公告解析、报告分析、风险监控和合规检查等金融场景。
---

# 实体识别 Skill

## 数据来源

本 Skill 支持多种金融文本数据输入，核心数据来源包括：

### 1. 金融文档类型
- **上市公司公告**：年报、季报、重大事项公告、权益变动报告
- **研究报告**：券商研报、行业分析报告、投资价值分析报告
- **监管文件**：证监会公告、交易所通知、行政处罚决定书
- **新闻资讯**：财经新闻、行业动态、公司新闻
- **合同协议**：贷款合同、担保合同、投资协议、并购协议

### 2. 文本格式支持
- **纯文本格式**：.txt 文件，UTF-8编码
- **结构化文档**：PDF、Word、Excel文档（需预处理为文本）
- **HTML网页**：财经网站页面内容
- **数据库文本字段**：从数据库直接读取的文本内容

### 3. 实体字典与规则库
- **标准实体字典**：包含上市公司列表、金融机构名录、金融产品分类
- **自定义实体字典**：用户可导入特定领域的实体名称列表
- **正则规则库**：用于识别特定格式的实体（如股票代码、证件号码）
- **行业术语库**：金融行业专业术语和缩写

> 说明：本 Skill 主要基于规则和字典匹配进行实体识别，对于复杂语境下的实体消歧和关系抽取能力有限。建议结合上下文分析和人工复核使用。

---

## 功能

本 Skill 提供全面的金融实体识别能力，涵盖四大类实体类型：

### 1. 主体实体识别
- **公司主体**：上市公司、非上市公司、集团公司、子公司
- **金融机构**：银行、证券公司、保险公司、基金公司、信托公司
- **监管机构**：证监会、银保监会、人民银行、交易所、行业协会
- **关键人物**：法定代表人、董事、监事、高级管理人员、实际控制人

### 2. 产品实体识别
- **金融产品**：股票、债券、基金、理财产品、衍生品
- **信贷产品**：贷款、信用证、保函、承兑汇票
- **保险产品**：财产保险、人寿保险、健康保险、责任保险
- **资管产品**：信托计划、资管计划、私募基金

### 3. 数值实体识别
- **金额实体**：人民币金额、外币金额、大写金额
- **比例实体**：百分比、千分比、增长率、占比
- **日期实体**：公告日期、生效日期、到期日期、报告期间
- **数量实体**：股份数量、交易数量、持仓数量

### 4. 事件实体识别
- **公司事件**：并购重组、股权变更、重大投资、诉讼仲裁
- **市场事件**：股价异常波动、停复牌、退市风险警示
- **监管事件**：行政处罚、监管措施、问询函、关注函
- **风险事件**：违约事件、担保代偿、资产查封、破产重整

### 5. 高级处理功能
- **实体归一化**：将不同表述的同一实体统一为标准名称
- **实体消歧**：根据上下文区分同名实体的不同指代
- **关系抽取**：识别实体之间的关联关系（持股、担保、交易等）
- **属性抽取**：提取实体的关键属性（注册资本、成立日期、注册地址等）
- **置信度评分**：为每个识别结果提供置信度评分

---

## 使用示例

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基础使用
```bash
# 识别文本中的实体
python scripts/recognize_entities.py --input announcement.txt --output entities.json

# 指定识别的实体类型
python scripts/recognize_entities.py --input report.txt --output companies.json --entity-type company

# 使用自定义实体字典
python scripts/recognize_entities.py --input text.txt --output results.json --dictionary custom_dict.csv
```

### 3. 批量处理
```bash
# 批量处理多个文件
python scripts/batch_recognize.py --input-dir ./documents --output-dir ./results --format json

# 处理PDF文档（需先转换为文本）
python scripts/process_pdf.py --input document.pdf --output text.txt
python scripts/recognize_entities.py --input text.txt --output entities.json
```

### 4. 高级配置
```bash
# 设置置信度阈值
python scripts/recognize_entities.py --input text.txt --output results.json --confidence-threshold 0.8

# 启用实体消歧
python scripts/recognize_entities.py --input text.txt --output results.json --disambiguation true

# 导出可视化结果
python scripts/recognize_entities.py --input text.txt --output visualization.html --format html
```

### 5. 输出示例
```json
{
  "document_id": "announcement_20250315_001",
  "source_file": "announcement.txt",
  "processing_time": "2025-03-15T17:50:00",
  "entities": [
    {
      "text": "贵州茅台酒股份有限公司",
      "type": "company",
      "subtype": "listed_company",
      "normalized_name": "贵州茅台",
      "stock_code": "600519",
      "confidence": 0.95,
      "position": {
        "start": 120,
        "end": 130,
        "sentence": "贵州茅台酒股份有限公司发布2024年度报告"
      },
      "attributes": {
        "industry": "白酒制造",
        "exchange": "上海证券交易所"
      }
    },
    {
      "text": "人民币100亿元",
      "type": "amount",
      "subtype": "rmb_amount",
      "normalized_value": 10000000000,
      "currency": "CNY",
      "confidence": 0.98,
      "position": {
        "start": 250,
        "end": 260,
        "sentence": "公司拟向全体股东每10股派发现金红利人民币100亿元"
      }
    },
    {
      "text": "中国证券监督管理委员会",
      "type": "regulatory_body",
      "subtype": "securities_regulator",
      "normalized_name": "证监会",
      "abbreviation": "CSRC",
      "confidence": 0.99,
      "position": {
        "start": 350,
        "end": 365,
        "sentence": "根据中国证券监督管理委员会的相关规定"
      }
    }
  ],
  "statistics": {
    "total_entities": 45,
    "by_type": {
      "company": 12,
      "amount": 8,
      "date": 10,
      "regulatory_body": 3,
      "person": 7,
      "product": 5
    },
    "average_confidence": 0.92
  },
  "relationships": [
    {
      "source": "贵州茅台",
      "target": "丁雄军",
      "relation": "chairman_of",
      "confidence": 0.88,
      "evidence": "丁雄军先生担任贵州茅台酒股份有限公司董事长"
    }
  ]
}
```

---

## 注意事项与限制

### 1. 识别准确性
- 规则匹配方法对规范文本识别准确率较高
- 对于口语化、缩写、错别字的识别能力有限
- 建议对关键实体进行人工复核

### 2. 上下文依赖
- 实体识别结果受上下文影响较大
- 同一实体在不同语境下可能有不同含义
- 建议结合篇章级分析提高准确性

### 3. 领域适应性
- 本 Skill 主要针对金融领域优化
- 对于其他专业领域（医疗、法律等）识别效果可能下降
- 可通过自定义字典提升特定领域识别能力

### 4. 性能考虑
- 大文档处理可能需要较长时间
- 内存占用与文档大小成正比
- 建议对超大文档进行分块处理

### 5. 使用限制
- 本 Skill 不包含深度学习模型，主要基于规则和字典
- 对于新兴实体和网络用语识别能力有限
- 实体关系抽取为初步结果，需进一步验证

### 6. 合规要求
- 处理敏感信息时需遵守数据保护法规
- 涉及个人信息的实体识别需获得授权
- 输出结果的使用应符合相关法律法规

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 金融实体分类体系
  - 实体识别规则手册
  - 金融术语词典
  - 性能优化指南
  - 合规使用说明

## License
- 本 skill 代码部分采用 MIT License，详见 `LICENSE` 文件
- 依赖与运行环境以 `requirements.txt` 为准
- 文档内容采用 CC BY 4.0 许可
