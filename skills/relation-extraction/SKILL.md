---
name: relation-extraction
description: 用于主体关系抽取的关系抽取原子 skill，适用于通用行业信息抽取场景。
---

# 关系抽取 Skill

## 数据来源

本 Skill 支持多种金融文本数据输入格式，核心数据来源包括：

### 1. 金融文档类型
- **公告文档**：上市公司公告、重大事项公告
- **合同文档**：贷款合同、担保合同、投资协议
- **报告文档**：研究报告、分析报告、尽职调查报告
- **新闻文档**：财经新闻、行业新闻、公司新闻

### 2. 文本数据格式
- **纯文本格式**：.txt 文件，UTF-8编码
- **结构化文档**：PDF、Word、Excel文档（需预处理为文本）
- **HTML网页**：财经网站页面内容
- **数据库文本字段**：从数据库直接读取的文本内容

### 3. 关系类型
- **股权关系**：持股关系、控股关系、参股关系
- **担保关系**：保证关系、抵押关系、质押关系
- **交易关系**：买卖关系、租赁关系、合作关系
- **关联关系**：关联方关系、关联交易关系

### 4. 数据格式要求
- **文件路径**：本地文件路径或网络文件URL
- **文件编码**：UTF-8、GBK、GB2312等
- **数据完整性**：需要包含完整的关系相关信息

> 说明：本 Skill 不包含数据采集功能，需要用户提供清洗后的文本数据。建议文档包含完整的关系描述，以便进行准确的关系抽取。

---

## 功能

本 Skill 提供全面的关系抽取能力，涵盖多种抽取功能：

### 1. 关系类型识别
- **股权关系识别**：识别股权相关关系
- **担保关系识别**：识别担保相关关系
- **交易关系识别**：识别交易相关关系
- **关联关系识别**：识别关联方关系

### 2. 关系主体抽取
- **关系主体识别**：识别关系的参与主体
- **主体角色识别**：识别主体在关系中的角色
- **主体属性提取**：提取主体的相关属性
- **主体归一化**：归一化主体名称

### 3. 关系属性抽取
- **关系类型**：识别关系的具体类型
- **关系强度**：评估关系的强度
- **关系时间**：抽取关系的起止时间
- **关系金额**：抽取关系涉及的金额

### 4. 关系描述抽取
- **关系描述**：抽取关系的详细描述
- **关系条件**：抽取关系的条件和约束
- **关系状态**：识别关系的状态和进展
- **关系影响**：评估关系的影响和后果

### 5. 关系网络构建
- **关系图构建**：构建实体关系图
- **关系路径发现**：发现实体之间的路径
- **关系聚类**：对关系进行聚类分析
- **关系可视化**：可视化关系网络

### 6. 高级处理功能
- **关系去重**：识别和合并相似关系
- **关系验证**：验证关系的准确性
- **关系补全**：补全缺失的关系信息
- **关系预测**：预测潜在的关系

---

## 使用示例

### 输出示例
```json
{
  "source_info": {
    "document_id": "DOC001",
    "document_type": "announcement",
    "source_file": "announcement.pdf"
  },
  "relations": [
    {
      "relation_id": "REL001",
      "relation_type": "shareholding",
      "relation_subtype": "direct_holding",
      "source_entity": {
        "type": "company",
        "name": "公司A",
        "normalized_name": "公司A股份有限公司"
      },
      "target_entity": {
        "type": "company",
        "name": "公司B",
        "normalized_name": "公司B股份有限公司"
      },
      "relation_properties": {
        "shareholding_ratio": 30.5,
        "shareholding_amount": 100000000,
        "shareholding_type": "流通股",
        "start_date": "2020-01-15",
        "end_date": null
      },
      "relation_description": "公司A持有公司B 30.5%的股份",
      "confidence": 0.95,
      "evidence": "根据公告，公司A持有公司B 30.5%的股份",
      "status": "active"
    },
    {
      "relation_id": "REL002",
      "relation_type": "guarantee",
      "relation_subtype": "guarantee_obligation",
      "source_entity": {
        "type": "company",
        "name": "公司C",
        "normalized_name": "公司C股份有限公司"
      },
      "target_entity": {
        "type": "company",
        "name": "公司D",
        "normalized_name": "公司D股份有限公司"
      },
      "relation_properties": {
        "guarantee_amount": 50000000,
        "guarantee_type": "连带责任保证",
        "start_date": "2023-06-01",
        "end_date": "2025-06-01"
      },
      "relation_description": "公司C为公司D提供5000万元连带责任保证",
      "confidence": 0.92,
      "evidence": "根据担保合同，公司C为公司D提供5000万元连带责任保证",
      "status": "active"
    }
  ],
  "relation_network": {
    "nodes": [
      {"id": "公司A", "type": "company"},
      {"id": "公司B", "type": "company"},
      {"id": "公司C", "type": "company"},
      {"id": "公司D", "type": "company"}
    ],
    "edges": [
      {
        "source": "公司A",
        "target": "公司B",
        "relation_type": "shareholding",
        "weight": 30.5
      },
      {
        "source": "公司C",
        "target": "公司D",
        "relation_type": "guarantee",
        "weight": 50000000
      }
    ]
  },
  "statistics": {
    "total_relations": 2,
    "relation_types": ["shareholding", "guarantee"],
    "entity_count": 4
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 文档需要包含关系相关信息
- 关系描述需要清晰明确
- 实体信息需要准确

### 2. 关系识别准确性
- 明确描述的关系识别准确率较高
- 隐含关系可能需要上下文分析
- 复杂关系可能需要人工分析

### 3. 实体识别准确性
- 标准实体名称识别准确率较高
- 非标准实体名称可能需要归一化
- 实体消歧可能需要额外处理

### 4. 关系类型分类
- 标准关系类型识别准确率较高
- 非标准关系可能需要人工分类
- 关系类型边界可能模糊

### 5. 使用限制
- 本 Skill 不包含关系分析功能
- 抽取结果需要人工复核
- 复杂关系可能需要人工分析

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 关系抽取方法手册
  - 关系类型分类体系
  - 实体归一化指南
  - 性能优化指南
