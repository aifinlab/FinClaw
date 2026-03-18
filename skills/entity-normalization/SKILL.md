---
name: entity-normalization
description: 用于实体归一的实体标准化原子 skill，适用于通用行业信息抽取场景。
---

# 实体标准化 Skill

## 数据来源

本 Skill 支持多种实体数据输入格式，核心数据来源包括：

### 1. 实体数据来源
- **实体识别结果**：从文本中识别出的实体
- **实体列表**：已有的实体列表和实体库
- **数据库记录**：数据库中的实体记录
- **API接口数据**：通过API获取的实体数据

### 2. 实体类型
- **公司实体**：公司名称、机构名称
- **人物实体**：人名、职位名称
- **产品实体**：产品名称、服务名称
- **地点实体**：地名、地址

### 3. 数据格式要求
- **JSON格式**：结构化的实体数据
- **CSV格式**：表格格式的实体数据
- **文本格式**：纯文本实体列表
- **数据库连接**：支持SQL数据库直接查询

### 4. 实体特征
- **实体名称**：实体的名称和别名
- **实体类型**：实体的类型和类别
- **实体属性**：实体的相关属性
- **实体上下文**：实体的上下文信息

> 说明：本 Skill 不包含实体识别功能，需要用户提供已识别的实体数据。建议实体数据包含足够的上下文信息，以便进行准确的标准化。

---

## 功能

本 Skill 提供全面的实体标准化能力，涵盖多种标准化功能：

### 1. 实体名称标准化
- **名称归一化**：将不同表述的实体名称统一为标准名称
- **别名识别**：识别实体的别名和简称
- **名称纠错**：纠正实体名称中的错误
- **名称补全**：补全实体名称的缺失部分

### 2. 实体类型标准化
- **类型分类**：对实体进行类型分类
- **类型映射**：将非标准类型映射到标准类型
- **类型验证**：验证实体类型的正确性
- **类型补全**：补全缺失的实体类型

### 3. 实体属性标准化
- **属性提取**：提取实体的标准属性
- **属性映射**：将非标准属性映射到标准属性
- **属性验证**：验证实体属性的正确性
- **属性补全**：补全缺失的实体属性

### 4. 实体消歧
- **同名实体区分**：区分同名但不同的实体
- **实体合并**：合并指向同一实体的不同表述
- **实体链接**：将实体链接到知识库
- **实体验证**：验证实体的唯一性

### 5. 实体匹配
- **相似实体匹配**：匹配相似的实体
- **模糊匹配**：支持模糊实体匹配
- **精确匹配**：支持精确实体匹配
- **匹配评分**：提供匹配评分和置信度

### 6. 高级处理功能
- **批量标准化**：批量处理多个实体
- **增量标准化**：增量更新实体标准化结果
- **标准化规则**：支持自定义标准化规则
- **标准化报告**：生成标准化报告和统计

---

## 使用示例

### 输出示例
```json
{
  "input_entities": [
    {
      "entity_id": "ENT001",
      "original_name": "中国工商银行",
      "entity_type": "bank",
      "context": "公告中提到中国工商银行"
    },
    {
      "entity_id": "ENT002",
      "original_name": "工商银行",
      "entity_type": "bank",
      "context": "工商银行发布公告"
    },
    {
      "entity_id": "ENT003",
      "original_name": "ICBC",
      "entity_type": "bank",
      "context": "ICBC的财务报告"
    }
  ],
  "normalized_entities": [
    {
      "entity_id": "ENT001",
      "original_name": "中国工商银行",
      "normalized_name": "中国工商银行股份有限公司",
      "standard_name": "中国工商银行",
      "aliases": ["工商银行", "ICBC", "工行"],
      "entity_type": "bank",
      "standard_type": "bank",
      "normalized_attributes": {
        "full_name": "中国工商银行股份有限公司",
        "short_name": "工商银行",
        "english_name": "Industrial and Commercial Bank of China",
        "abbreviation": "ICBC",
        "stock_code": "601398"
      },
      "confidence": 0.98,
      "match_method": "exact_match"
    },
    {
      "entity_id": "ENT002",
      "original_name": "工商银行",
      "normalized_name": "中国工商银行股份有限公司",
      "standard_name": "中国工商银行",
      "aliases": ["工商银行", "ICBC", "工行"],
      "entity_type": "bank",
      "standard_type": "bank",
      "normalized_attributes": {
        "full_name": "中国工商银行股份有限公司",
        "short_name": "工商银行",
        "english_name": "Industrial and Commercial Bank of China",
        "abbreviation": "ICBC",
        "stock_code": "601398"
      },
      "confidence": 0.95,
      "match_method": "alias_match"
    },
    {
      "entity_id": "ENT003",
      "original_name": "ICBC",
      "normalized_name": "中国工商银行股份有限公司",
      "standard_name": "中国工商银行",
      "aliases": ["工商银行", "ICBC", "工行"],
      "entity_type": "bank",
      "standard_type": "bank",
      "normalized_attributes": {
        "full_name": "中国工商银行股份有限公司",
        "short_name": "工商银行",
        "english_name": "Industrial and Commercial Bank of China",
        "abbreviation": "ICBC",
        "stock_code": "601398"
      },
      "confidence": 0.92,
      "match_method": "abbreviation_match"
    }
  ],
  "entity_mapping": {
    "ENT001": "NORM001",
    "ENT002": "NORM001",
    "ENT003": "NORM001"
  },
  "statistics": {
    "input_count": 3,
    "normalized_count": 1,
    "merge_count": 2,
    "average_confidence": 0.95
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 实体数据需要包含足够的上下文信息
- 实体名称需要清晰明确
- 实体类型需要准确

### 2. 标准化准确性
- 标准实体名称标准化准确率较高
- 非标准实体名称可能需要人工处理
- 实体消歧可能需要额外信息

### 3. 实体匹配
- 精确匹配准确率较高
- 模糊匹配可能需要人工复核
- 相似实体匹配可能产生误匹配

### 4. 知识库依赖
- 标准化结果依赖知识库的完整性
- 知识库更新可能影响标准化结果
- 新实体可能需要人工处理

### 5. 使用限制
- 本 Skill 不包含实体识别功能
- 标准化结果需要人工复核
- 复杂实体可能需要人工处理

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 实体标准化方法手册
  - 实体匹配算法说明
  - 实体消歧指南
  - 性能优化指南
