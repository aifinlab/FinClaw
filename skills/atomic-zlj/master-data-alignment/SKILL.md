---
name: master-data-alignment
description: 用于主键统一的实体主数据对齐原子 skill，适用于通用行业数据接入场景。
---

# 实体主数据对齐 Skill

## 数据来源

本 Skill 支持多种实体主数据输入格式，核心数据来源包括：

### 1. 数据源类型
- **数据库**：多个不同结构的数据库
- **API接口**：多个不同格式的API接口
- **文件数据**：多个不同格式的文件
- **系统数据**：多个不同系统的数据

### 2. 实体类型
- **公司实体**：公司名称、公司代码、统一社会信用代码
- **产品实体**：产品名称、产品代码、产品ID
- **客户实体**：客户名称、客户代码、客户ID
- **账户实体**：账户名称、账户代码、账户ID

### 3. 数据格式要求
- **源数据**：需要对齐的源数据
- **主数据标准**：主数据标准定义和规范
- **对齐规则**：实体对齐规则和匹配规则
- **主键映射**：主键映射关系

### 4. 对齐特征
- **对齐类型**：精确匹配、模糊匹配、规则匹配
- **对齐复杂度**：简单对齐、复杂对齐
- **对齐范围**：部分实体对齐、全实体对齐
- **对齐准确性**：高准确率对齐、低准确率对齐

> 说明：本 Skill 不包含数据采集功能，需要用户提供源数据和主数据标准。建议主数据标准清晰明确，以便进行准确的实体对齐。

---

## 功能

本 Skill 提供全面的实体主数据对齐能力，涵盖多种对齐功能：

### 1. 实体识别
- **实体提取**：从数据源中提取实体信息
- **实体分类**：对实体进行分类和标签化
- **实体去重**：识别和去除重复实体
- **实体标准化**：标准化实体名称和格式

### 2. 主键统一
- **主键识别**：识别实体的主键字段
- **主键映射**：映射不同数据源的主键
- **主键生成**：为实体生成统一主键
- **主键验证**：验证主键的唯一性和有效性

### 3. 实体对齐
- **精确匹配**：精确匹配相同实体
- **模糊匹配**：模糊匹配相似实体
- **规则匹配**：基于规则匹配实体
- **关联匹配**：基于关联关系匹配实体

### 4. 主数据管理
- **主数据创建**：创建主数据记录
- **主数据更新**：更新主数据记录
- **主数据合并**：合并重复主数据
- **主数据删除**：删除无效主数据

### 5. 数据验证
- **对齐完整性验证**：验证对齐的完整性
- **对齐准确性验证**：验证对齐的准确性
- **主键唯一性验证**：验证主键的唯一性
- **数据一致性验证**：验证数据的一致性

### 6. 高级处理功能
- **批量对齐**：批量处理多个实体对齐
- **增量对齐**：增量更新实体对齐
- **对齐报告**：生成实体对齐报告
- **对齐监控**：监控对齐过程和结果

---

## 使用示例

### 输出示例
```json
{
  "source_info": {
    "source_data": "company_data.csv",
    "source_format": "csv",
    "entity_count": 1000
  },
  "master_data_standard": {
    "standard_name": "company_master_data",
    "primary_key": "company_code",
    "key_fields": ["company_name", "unified_social_credit_code"]
  },
  "alignment_rules": [
    {
      "rule_id": "RULE001",
      "rule_type": "exact_match",
      "match_fields": ["company_name"],
      "confidence_threshold": 1.0
    },
    {
      "rule_id": "RULE002",
      "rule_type": "fuzzy_match",
      "match_fields": ["company_name"],
      "confidence_threshold": 0.9
    }
  ],
  "alignment_results": {
    "total_entities": 1000,
    "aligned_entities": 950,
    "unmatched_entities": 50,
    "alignment_time": "2024-03-15T10:00:00",
    "duration": "30s"
  },
  "aligned_entities": [
    {
      "source_entity": {
        "source_id": "SRC001",
        "company_name": "示例股份有限公司",
        "source_key": "COMP001"
      },
      "master_entity": {
        "master_id": "MAST001",
        "company_code": "COMP001",
        "company_name": "示例股份有限公司",
        "unified_social_credit_code": "91110000123456789X"
      },
      "alignment_type": "exact_match",
      "confidence": 1.0,
      "match_fields": ["company_name"]
    }
  ],
  "statistics": {
    "entities_aligned": 950,
    "entities_unmatched": 50,
    "exact_matches": 800,
    "fuzzy_matches": 150,
    "alignment_accuracy": 0.95
  }
}
```

---

## 注意事项与限制

### 1. 主数据标准要求
- 主数据标准需要清晰明确
- 主键定义需要唯一且稳定
- 标准字段需要完整

### 2. 对齐准确性
- 精确匹配准确率较高
- 模糊匹配可能需要人工复核
- 复杂实体可能需要特殊处理

### 3. 主键统一
- 主键需要保证唯一性
- 主键映射需要准确
- 主键生成需要遵循规则

### 4. 数据一致性
- 需要保证对齐后数据一致性
- 需要验证对齐结果
- 异常数据需要处理

### 5. 使用限制
- 本 Skill 不包含数据采集功能
- 对齐结果需要人工复核
- 复杂实体可能需要特殊处理

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 实体主数据对齐方法手册
  - 主数据标准规范定义
  - 对齐规则配置指南
  - 性能优化指南
