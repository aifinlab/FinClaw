---
name: financial-report-layout-parsing
description: 用于三表/附注拆分的财报版式解析原子 skill，适用于通用行业文档解析场景。
---

# 财报版式解析 Skill

## 数据来源

本 Skill 支持多种财务报表输入格式，核心数据来源包括：

### 1. 财务报表类型
- **年度报告**：年度财务报告
- **季度报告**：季度财务报告
- **半年度报告**：半年度财务报告
- **临时报告**：临时财务报告

### 2. 文档格式
- **PDF格式**：PDF格式的财务报表
- **Word格式**：Word格式的财务报表
- **Excel格式**：Excel格式的财务报表
- **HTML格式**：网页格式的财务报表

### 3. 报表结构
- **利润表**：利润表部分
- **资产负债表**：资产负债表部分
- **现金流量表**：现金流量表部分
- **财务报表附注**：财务报表附注部分

### 4. 数据格式要求
- **文件路径**：本地文件路径或网络文件URL
- **文件编码**：UTF-8、GBK、GB2312等
- **文件权限**：需要读取权限

> 说明：本 Skill 不包含文档采集功能，需要用户提供财务报表文件。建议报表格式规范，以便进行准确的版式解析。

---

## 功能

本 Skill 提供全面的财报版式解析能力，涵盖多种解析功能：

### 1. 报表结构识别
- **报表类型识别**：识别报表的类型和期间
- **报表章节识别**：识别报表的章节结构
- **报表页面识别**：识别报表的页面布局
- **报表区域识别**：识别报表的不同区域

### 2. 三大报表识别
- **利润表识别**：识别和提取利润表
- **资产负债表识别**：识别和提取资产负债表
- **现金流量表识别**：识别和提取现金流量表
- **报表关联识别**：识别报表之间的关联关系

### 3. 附注识别
- **附注章节识别**：识别附注的章节结构
- **附注内容提取**：提取附注的具体内容
- **附注表格识别**：识别附注中的表格
- **附注关联识别**：识别附注与报表的关联

### 4. 表格结构解析
- **表格定位**：定位报表中的表格位置
- **表格结构识别**：识别表格的行列结构
- **表格内容提取**：提取表格的具体内容
- **表格格式保留**：保留表格的格式信息

### 5. 版式还原
- **版式结构还原**：尽可能还原报表的原始版式
- **格式信息保留**：保留字体、字号等格式信息
- **布局信息记录**：记录页面布局和元素位置
- **版式标准化**：标准化报表版式

### 6. 高级处理功能
- **报表拆分**：拆分报表的不同部分
- **报表合并**：合并报表的不同部分
- **报表验证**：验证报表的完整性
- **报表报告**：生成报表解析报告

---

## 使用示例

### 输出示例
```json
{
  "source_info": {
    "document_id": "DOC001",
    "document_type": "annual_report",
    "report_period": "2024",
    "source_file": "annual_report.pdf",
    "page_count": 200
  },
  "report_structure": {
    "sections": [
      {
        "section_id": "SEC001",
        "section_name": "利润表",
        "section_type": "income_statement",
        "start_page": 50,
        "end_page": 52,
        "tables": [
          {
            "table_id": "TBL001",
            "table_type": "income_statement",
            "position": {
              "page": 50,
              "bbox": [100, 200, 500, 600]
            },
            "row_count": 30,
            "column_count": 5
          }
        ]
      },
      {
        "section_id": "SEC002",
        "section_name": "资产负债表",
        "section_type": "balance_sheet",
        "start_page": 53,
        "end_page": 55,
        "tables": [
          {
            "table_id": "TBL002",
            "table_type": "balance_sheet",
            "position": {
              "page": 53,
              "bbox": [100, 200, 500, 700]
            },
            "row_count": 50,
            "column_count": 5
          }
        ]
      },
      {
        "section_id": "SEC003",
        "section_name": "现金流量表",
        "section_type": "cash_flow_statement",
        "start_page": 56,
        "end_page": 58,
        "tables": [
          {
            "table_id": "TBL003",
            "table_type": "cash_flow_statement",
            "position": {
              "page": 56,
              "bbox": [100, 200, 500, 600]
            },
            "row_count": 25,
            "column_count": 5
          }
        ]
      },
      {
        "section_id": "SEC004",
        "section_name": "财务报表附注",
        "section_type": "notes",
        "start_page": 59,
        "end_page": 200,
        "subsections": [
          {
            "subsection_name": "一、公司基本情况",
            "start_page": 59,
            "end_page": 65
          },
          {
            "subsection_name": "二、财务报表编制基础",
            "start_page": 66,
            "end_page": 70
          }
        ]
      }
    ]
  },
  "statistics": {
    "total_sections": 4,
    "total_tables": 3,
    "total_pages": 200,
    "parsing_confidence": 0.95
  }
}
```

---

## 注意事项与限制

### 1. 报表格式要求
- 标准格式报表解析准确率较高
- 非标准格式可能影响解析
- 扫描版报表需要OCR支持

### 2. 报表结构识别
- 标准报表结构识别准确率较高
- 非标准结构可能需要人工处理
- 复杂结构可能需要人工分析

### 3. 表格识别准确性
- 标准表格识别准确率较高
- 复杂表格可能需要人工处理
- 合并单元格可能影响识别

### 4. 附注解析
- 标准附注格式解析准确率较高
- 非标准附注可能需要人工处理
- 复杂附注可能需要人工分析

### 5. 使用限制
- 本 Skill 不包含报表编辑功能
- 解析结果需要人工复核
- 复杂报表可能需要人工处理

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 财报版式解析方法手册
  - 财务报表结构标准
  - 表格识别算法说明
  - 性能优化指南
