---
name: product-feature-extraction
description: 用于产品属性抽取的产品特征抽取原子 skill，适用于通用行业信息抽取场景。
---

# 产品特征抽取 Skill

## 数据来源

本 Skill 支持多种产品数据输入格式，核心数据来源包括：

### 1. 产品文档类型
- **产品说明书**：产品使用说明书、技术规格书
- **产品介绍**：产品介绍文档、宣传材料
- **产品目录**：产品目录、产品清单
- **产品评论**：产品评论、用户评价

### 2. 文本数据格式
- **纯文本格式**：.txt 文件，UTF-8编码
- **结构化文档**：PDF、Word、Excel文档（需预处理为文本）
- **HTML网页**：产品网页内容
- **数据库文本字段**：从数据库直接读取的文本内容

### 3. 数据格式要求
- **文件路径**：本地文件路径或网络文件URL
- **文件编码**：UTF-8、GBK、GB2312等
- **数据完整性**：需要包含完整的产品信息

### 4. 产品类型
- **金融产品**：理财产品、保险产品、基金产品
- **实物产品**：商品、设备、材料
- **服务产品**：服务项目、服务套餐
- **数字产品**：软件、应用、平台

> 说明：本 Skill 不包含数据采集功能，需要用户提供产品相关文档。建议文档包含完整的产品信息，以便进行准确的特征抽取。

---

## 功能

本 Skill 提供全面的产品特征抽取能力，涵盖多种抽取功能：

### 1. 产品基本信息抽取
- **产品名称**：抽取产品名称和型号
- **产品分类**：抽取产品分类和类别
- **产品描述**：抽取产品描述和说明
- **产品规格**：抽取产品规格和参数

### 2. 产品属性抽取
- **物理属性**：尺寸、重量、颜色等物理属性
- **功能属性**：功能特性、性能指标等功能属性
- **价格属性**：价格、折扣、优惠等价格属性
- **时间属性**：上市时间、有效期等时间属性

### 3. 产品特征识别
- **核心特征**：识别产品的核心特征
- **优势特征**：识别产品的优势特征
- **特色特征**：识别产品的特色特征
- **差异化特征**：识别产品的差异化特征

### 4. 产品关系抽取
- **产品关联**：抽取产品之间的关联关系
- **产品组合**：识别产品组合和套餐
- **产品替代**：识别产品的替代产品
- **产品配套**：识别产品的配套产品

### 5. 产品标签生成
- **特征标签**：为产品生成特征标签
- **分类标签**：为产品生成分类标签
- **应用标签**：为产品生成应用场景标签
- **用户标签**：为产品生成用户群体标签

### 6. 高级处理功能
- **特征标准化**：标准化产品特征
- **特征对比**：对比不同产品的特征
- **特征推荐**：基于特征推荐相似产品
- **特征报告**：生成产品特征报告

---

## 使用示例

### 输出示例
```json
{
  "source_info": {
    "document_id": "DOC001",
    "document_type": "product_specification",
    "source_file": "product_spec.pdf"
  },
  "product_info": {
    "product_name": "示例理财产品",
    "product_code": "PRD001",
    "product_type": "financial_product",
    "product_category": "理财产品",
    "product_description": "一款稳健型理财产品，适合风险承受能力较低的投资者"
  },
  "features": [
    {
      "feature_id": "FEAT001",
      "feature_name": "预期收益率",
      "feature_type": "performance",
      "feature_value": "4.5%",
      "feature_unit": "%",
      "feature_category": "收益特征",
      "confidence": 0.98
    },
    {
      "feature_id": "FEAT002",
      "feature_name": "投资期限",
      "feature_type": "time",
      "feature_value": "365",
      "feature_unit": "天",
      "feature_category": "期限特征",
      "confidence": 0.95
    },
    {
      "feature_id": "FEAT003",
      "feature_name": "风险等级",
      "feature_type": "risk",
      "feature_value": "R2",
      "feature_unit": null,
      "feature_category": "风险特征",
      "confidence": 0.97
    },
    {
      "feature_id": "FEAT004",
      "feature_name": "起购金额",
      "feature_type": "amount",
      "feature_value": "10000",
      "feature_unit": "CNY",
      "feature_category": "门槛特征",
      "confidence": 0.96
    }
  ],
  "attributes": {
    "physical_attributes": [],
    "functional_attributes": [
      {"name": "预期收益率", "value": "4.5%"},
      {"name": "风险等级", "value": "R2"}
    ],
    "price_attributes": [
      {"name": "起购金额", "value": "10000 CNY"}
    ],
    "time_attributes": [
      {"name": "投资期限", "value": "365天"}
    ]
  },
  "tags": [
    "稳健型",
    "低风险",
    "中长期",
    "理财产品"
  ],
  "statistics": {
    "total_features": 15,
    "extracted_features": 14,
    "missing_features": 1,
    "average_confidence": 0.96
  }
}
```

---

## 注意事项与限制

### 1. 文档质量要求
- 文档需要包含产品相关信息
- 产品描述需要清晰明确
- 产品特征需要完整

### 2. 特征识别准确性
- 明确描述的特征识别准确率较高
- 隐含特征可能需要上下文分析
- 复杂特征可能需要人工处理

### 3. 产品类型差异
- 不同类型产品的特征差异较大
- 需要针对不同类型产品建立特征模型
- 新类型产品可能需要人工处理

### 4. 特征标准化
- 标准特征名称标准化准确率较高
- 非标准特征可能需要映射
- 特征值标准化需要正确处理

### 5. 使用限制
- 本 Skill 不包含产品分析功能
- 抽取结果需要人工复核
- 复杂产品可能需要人工处理

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 产品特征抽取方法手册
  - 产品特征分类体系
  - 特征标准化指南
  - 性能优化指南
