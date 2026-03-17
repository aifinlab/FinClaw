---
name: time-series-cleaning
description: 用于时序标准化的时间序列数据整理原子 skill，适用于通用行业数据接入场景。
---

# 时间序列数据整理 Skill

## 数据来源

本 Skill 支持多种时间序列数据输入格式，核心数据来源包括：

### 1. 数据源类型
- **数据库**：SQL数据库、NoSQL数据库
- **API接口**：REST API、GraphQL API
- **文件数据**：CSV文件、Excel文件、JSON文件
- **流式数据**：Kafka、RabbitMQ等消息队列

### 2. 时间序列类型
- **金融时间序列**：股价、汇率、利率等金融数据
- **业务时间序列**：销售额、用户数、订单数等业务数据
- **监控时间序列**：系统指标、性能指标等监控数据
- **传感器时间序列**：温度、湿度、压力等传感器数据

### 3. 数据格式要求
- **时间字段**：日期时间字段、时间戳字段
- **数值字段**：数值型数据字段
- **数据频率**：日度、周度、月度、年度等不同频率
- **数据完整性**：需要包含时间序列的基本信息

### 4. 数据特征
- **数据规模**：小数据集（<1000条）、大数据集（>100万条）
- **数据质量**：完整数据、缺失数据、异常数据
- **时间范围**：短期数据、长期数据、历史数据
- **数据格式**：标准格式、非标准格式

> 说明：本 Skill 不包含数据采集功能，需要用户提供时间序列数据。建议数据包含完整的时间信息，以便进行准确的数据整理。

---

## 功能

本 Skill 提供全面的时间序列数据整理能力，涵盖多种整理功能：

### 1. 数据清洗
- **缺失值处理**：识别和处理缺失值
- **异常值检测**：检测和处理异常值
- **重复值处理**：识别和处理重复值
- **数据格式转换**：转换数据格式和类型

### 2. 时间标准化
- **时间格式统一**：统一时间格式
- **时区处理**：处理时区转换
- **时间频率转换**：转换时间频率
- **时间对齐**：对齐不同时间序列的时间

### 3. 数据标准化
- **数值标准化**：标准化数值数据
- **单位统一**：统一数据单位
- **精度处理**：处理数据精度
- **数据归一化**：归一化数据范围

### 4. 数据补全
- **缺失值填充**：填充缺失值
- **插值处理**：使用插值方法补全数据
- **外推处理**：使用外推方法补全数据
- **数据重建**：重建缺失的数据点

### 5. 数据验证
- **数据完整性验证**：验证数据的完整性
- **数据准确性验证**：验证数据的准确性
- **数据一致性验证**：验证数据的一致性
- **数据质量评估**：评估数据的质量

### 6. 高级处理功能
- **数据转换**：转换数据格式和结构
- **数据聚合**：聚合时间序列数据
- **数据采样**：采样时间序列数据
- **数据报告**：生成数据整理报告

---

## 使用示例

### 输出示例
```json
{
  "source_info": {
    "data_source": "database",
    "table_name": "stock_prices",
    "time_field": "trade_date",
    "value_field": "close_price",
    "total_records": 10000
  },
  "cleaning_results": {
    "missing_values": {
      "count": 50,
      "percentage": 0.5,
      "handled": true,
      "method": "forward_fill"
    },
    "outliers": {
      "count": 20,
      "percentage": 0.2,
      "detected": true,
      "method": "iqr",
      "removed": false
    },
    "duplicates": {
      "count": 10,
      "percentage": 0.1,
      "removed": true
    }
  },
  "standardization_results": {
    "time_format": {
      "original": "YYYY-MM-DD",
      "standardized": "YYYY-MM-DD",
      "timezone": "UTC"
    },
    "value_format": {
      "original_unit": "元",
      "standardized_unit": "CNY",
      "precision": 2
    },
    "frequency": {
      "original": "daily",
      "standardized": "daily",
      "aligned": true
    }
  },
  "data_quality": {
    "completeness": 0.995,
    "accuracy": 0.98,
    "consistency": 0.97,
    "overall_score": 0.98
  },
  "cleaned_data": {
    "total_records": 9990,
    "time_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "sample_data": [
      {
        "time": "2024-01-01",
        "value": 100.50,
        "quality": "good"
      },
      {
        "time": "2024-01-02",
        "value": 101.20,
        "quality": "good"
      }
    ]
  },
  "statistics": {
    "processing_time": "5.2s",
    "records_processed": 10000,
    "records_cleaned": 9990,
    "records_removed": 10
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 数据需要包含时间信息
- 时间格式需要可识别
- 数值数据需要有效

### 2. 缺失值处理
- 不同处理方法结果可能不同
- 需要根据业务场景选择方法
- 缺失值过多可能影响结果

### 3. 异常值处理
- 异常值检测方法需要选择
- 异常值可能是真实数据
- 需要结合业务判断处理

### 4. 时间标准化
- 时间格式需要统一
- 时区处理需要正确
- 时间频率转换可能丢失信息

### 5. 使用限制
- 本 Skill 不包含数据分析功能
- 整理结果需要人工复核
- 复杂数据可能需要人工处理

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 时间序列数据整理方法手册
  - 缺失值处理方法说明
  - 异常值检测算法指南
  - 性能优化指南
