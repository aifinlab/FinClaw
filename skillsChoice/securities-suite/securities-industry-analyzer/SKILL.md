---
name: securities-industry-analyzer
description: 证券行业宏观分析工具。获取证券行业整体数据，包括证券公司数量、总资产、净资产、营业收入、净利润、行业集中度等。支持中证协、证监会官方数据查询，以及证券行业景气度分析。使用AkShare、中证协、证监会数据。适用于证券行业研究、政策分析、投资策略制定。
---

# 证券行业宏观分析器

## 功能

- 证券行业整体规模（总资产、净资产、营收、利润）
- 证券公司数量与结构
- 行业集中度分析（CR5、CR10）
- 行业盈利能力指标（ROE、利润率）
- 监管政策影响分析
- 行业景气度判断

## 数据源

- **AkShare**: 证券行业数据、券商行情
- **中国证券业协会**: 行业统计数据
- **证监会**: 监管数据、证券公司名录
- **交易所**: 成交额、市值数据

## 核心指标

| 指标 | 说明 | 数据来源 |
|------|------|----------|
| 行业总资产 | 证券公司资产合计 | 中证协 |
| 行业净资产 | 证券公司净资产合计 | 中证协 |
| 营业收入 | 全行业营业收入 | 中证协 |
| 净利润 | 全行业净利润 | 中证协 |
| 行业ROE | 净资产收益率 | 计算值 |
| 集中度CR5 | 前五家券商收入占比 | 计算值 |

## 使用方法

```python
from scripts.main import SecuritiesIndustryAnalyzer

analyzer = SecuritiesIndustryAnalyzer()
overview = analyzer.get_industry_overview()
concentration = analyzer.get_concentration_analysis()
```

## 依赖

- akshare >= 1.10.0
- pandas >= 1.3.0
- requests >= 2.28.0
