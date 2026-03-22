---
name: bank-financial-analyzer
description: 商业银行财务深度分析。分析个股银行（如招商银行、工商银行等）的财务报表，包括资产负债表、利润表、现金流量表核心指标。支持ROE/ROA分析、净息差、手续费收入占比、成本收入比等关键指标计算。使用同花顺iFinD API、Tushare Pro获取真实财报数据。适用于银行个股研究、投资决策、财务健康度评估。
---

# 商业银行财务分析器

## 功能

深度分析上市银行的财务状况：
- 资产负债表分析（总资产、存贷款规模、资本结构）
- 利润表分析（营收、净利润、收入结构）
- 现金流量分析（经营/投资/筹资现金流）
- 核心财务指标（ROE、ROA、NIM、成本收入比）
- 季度/年度对比分析
- 同业对比分析

## 数据源

- **同花顺iFinD API**: 实时行情、财务指标
- **Tushare Pro**: 详细财报数据（三大表）
- **AkShare**: 银行列表、基础数据

## 支持的银行

A股上市银行（42家）：
- 国有大行：工商银行、农业银行、中国银行、建设银行、交通银行、邮储银行
- 股份制银行：招商银行、兴业银行、浦发银行、中信银行、民生银行、光大银行、平安银行、华夏银行、浙商银行
- 城商行：北京银行、上海银行、江苏银行、南京银行、宁波银行等
- 农商行：渝农商行、沪农商行等

## 使用方法

### Python API

```python
from scripts.main import BankFinancialAnalyzer

analyzer = BankFinancialAnalyzer()

# 分析单家银行
result = analyzer.analyze_bank("招商银行")

# 对比多家银行
comparison = analyzer.compare_banks(["招商银行", "工商银行", "宁波银行"])

# 获取财务指标历史趋势
trend = analyzer.get_financial_trend("600036", metric="ROE", periods=8)
```

### CLI命令

```bash
# 分析单家银行
python scripts/main.py --bank "招商银行" --action analyze

# 对比多家银行
python scripts/main.py --banks "招商银行,工商银行,宁波银行" --action compare

# 查看ROE趋势
python scripts/main.py --code 600036 --action trend --metric ROE
```

## 核心指标

| 指标 | 计算公式 | 优秀标准 |
|------|----------|----------|
| ROE | 净利润/平均净资产 | >15% |
| ROA | 净利润/平均总资产 | >1% |
| 净息差(NIM) | 净利息收入/平均生息资产 | >2% |
| 成本收入比 | 业务及管理费/营业收入 | <35% |
| 非息收入占比 | 非利息收入/营业收入 | >30% |
| 每股净资产 | 净资产/总股本 | - |

## 依赖

- tushare >= 1.2.90
- akshare >= 1.10.0
- pandas >= 1.3.0
- numpy >= 1.21.0
