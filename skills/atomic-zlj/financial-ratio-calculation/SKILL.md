---
name: financial-ratio-calculation
description: 用于计算企业财务比率的原子技能，包括盈利能力、偿债能力、营运能力和成长性指标。适用于财务报表分析、企业信用评估、投资研究和风险管理等金融场景。
---

# 财务比率计算 Skill

## 数据来源

本 Skill 支持多种财务数据输入格式，核心数据来源包括：

### 1. 财务报表数据
- **利润表数据**：营业收入、营业成本、销售费用、管理费用、财务费用、净利润等
- **资产负债表数据**：资产总额、负债总额、所有者权益、流动资产、流动负债、存货、应收账款等
- **现金流量表数据**：经营活动现金流量、投资活动现金流量、筹资活动现金流量

### 2. 市场数据（可选）
- **股价数据**：用于计算市值相关比率
- **行业基准数据**：用于同业比较分析

### 3. 数据格式要求
- **CSV格式**：标准财务报表CSV文件，包含时间序列数据
- **Excel格式**：支持多工作表财务报表
- **JSON格式**：结构化财务数据
- **数据库连接**：支持SQL数据库直接查询

> 说明：本 Skill 不包含数据采集功能，需要用户提供清洗后的财务数据。建议数据时间跨度不少于3年，以便进行趋势分析。

---

## 功能

本 Skill 提供全面的财务比率计算能力，涵盖四大类财务指标：

### 1. 盈利能力指标
- **毛利率** = (营业收入 - 营业成本) / 营业收入 × 100%
- **净利率** = 净利润 / 营业收入 × 100%
- **净资产收益率(ROE)** = 净利润 / 平均净资产 × 100%
- **总资产收益率(ROA)** = 净利润 / 平均总资产 × 100%
- **投入资本回报率(ROIC)** = 税后净营业利润 / 投入资本 × 100%

### 2. 偿债能力指标
- **流动比率** = 流动资产 / 流动负债
- **速动比率** = (流动资产 - 存货) / 流动负债
- **现金比率** = 货币资金 / 流动负债
- **资产负债率** = 负债总额 / 资产总额 × 100%
- **利息保障倍数** = 息税前利润 / 利息费用

### 3. 营运能力指标
- **应收账款周转率** = 营业收入 / 平均应收账款
- **存货周转率** = 营业成本 / 平均存货
- **总资产周转率** = 营业收入 / 平均总资产
- **固定资产周转率** = 营业收入 / 平均固定资产

### 4. 成长性指标
- **营业收入增长率** = (本期营业收入 - 上期营业收入) / 上期营业收入 × 100%
- **净利润增长率** = (本期净利润 - 上期净利润) / 上期净利润 × 100%
- **总资产增长率** = (本期总资产 - 上期总资产) / 上期总资产 × 100%

### 5. 数据处理能力
- **缺失值处理**：支持均值填充、前向填充、插值等多种方法
- **异常值检测**：基于统计方法识别和处理异常值
- **数据标准化**：支持Min-Max标准化、Z-score标准化
- **行业调整**：支持按行业分类进行比率调整

---

## 使用示例

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基础使用
```bash
# 计算所有财务比率
python scripts/calc_ratios.py --input financials.csv --output ratios.csv

# 指定计算特定类型的比率
python scripts/calc_ratios.py --input financials.csv --output profitability.csv --ratio-type profitability

# 添加行业基准比较
python scripts/calc_ratios.py --input financials.csv --output analysis.csv --industry-benchmark manufacturing
```

### 3. 高级配置
```bash
# 自定义缺失值处理方法
python scripts/calc_ratios.py --input financials.csv --output ratios.csv --missing-method forward-fill

# 设置时间窗口进行滚动计算
python scripts/calc_ratios.py --input financials.csv --output rolling_ratios.csv --window 4 --min-periods 2

# 导出详细分析报告
python scripts/calc_ratios.py --input financials.csv --output report.html --format html --detailed
```

### 4. 输出示例
```json
{
  "company": "示例公司",
  "period": "2025",
  "profitability_ratios": {
    "gross_margin": 35.2,
    "net_margin": 12.8,
    "roe": 15.6,
    "roa": 8.3,
    "roic": 14.7
  },
  "liquidity_ratios": {
    "current_ratio": 1.8,
    "quick_ratio": 1.2,
    "cash_ratio": 0.4
  },
  "leverage_ratios": {
    "debt_to_assets": 45.3,
    "debt_to_equity": 82.7,
    "interest_coverage": 6.5
  },
  "efficiency_ratios": {
    "receivables_turnover": 8.2,
    "inventory_turnover": 6.7,
    "asset_turnover": 0.9
  },
  "growth_ratios": {
    "revenue_growth": 12.5,
    "net_income_growth": 18.3,
    "asset_growth": 8.7
  },
  "analysis": {
    "trend": "improving",
    "strengths": ["盈利能力持续改善", "营运效率提升"],
    "weaknesses": ["偿债压力较大", "现金流偏紧"],
    "recommendations": ["优化负债结构", "加强应收账款管理"]
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 财务报表数据需要经过审计或可靠来源
- 建议使用同一会计准则下的数据进行比较
- 非经常性损益项目需要单独处理

### 2. 行业差异考虑
- 不同行业的财务比率正常范围差异较大
- 重资产行业和轻资产行业的比率不可直接比较
- 建议使用行业调整后的比率进行分析

### 3. 时间序列分析
- 财务比率分析应结合趋势分析
- 季节性因素可能影响季度比率
- 经济周期对财务比率有显著影响

### 4. 综合判断原则
- 单一比率不能全面反映企业财务状况
- 需要结合多个比率进行综合分析
- 应结合非财务信息进行判断

### 5. 使用限制
- 本 Skill 输出为技术分析结果，不构成投资建议
- 使用者应结合专业判断和具体业务场景
- 对于重大决策，建议咨询专业财务顾问

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 财务比率计算公式手册
  - 行业基准比率参考值
  - 财务分析最佳实践指南
  - 数据处理方法说明文档

## License
- 本 skill 代码部分采用 MIT License，详见 `LICENSE` 文件
- 依赖与运行环境以 `requirements.txt` 为准
- 文档内容采用 CC BY 4.0 许可
