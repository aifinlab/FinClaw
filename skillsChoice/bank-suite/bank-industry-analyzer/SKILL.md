---
name: bank-industry-analyzer
description: 银行业宏观分析与行业研究。获取银行业整体数据，包括银行业金融机构数量、资产规模、存贷款余额、行业利润、不良贷款率、拨备覆盖率、资本充足率等核心指标。支持央行、银保监会官方数据查询，以及银行业景气度分析。使用AkShare、央行官网、银保监会数据。适用于银行行业研究、政策分析、投资策略制定。
---

# 银行业宏观分析器

## 功能

获取银行业整体运行数据，进行行业级分析：
- 银行业金融机构数量与结构
- 银行业资产规模与增长
- 存贷款余额与结构
- 银行业利润水平
- 资产质量指标（不良率、拨备覆盖率）
- 资本充足情况
- 政策解读与影响分析

## 数据源

- **AkShare**: 银行业基础数据、统计指标
- **中国人民银行**: 货币政策、存款准备金率、LPR
- **国家金融监督管理总局（原银保监会）**: 银行业监管统计数据

## 使用方法

### 查询银行业整体数据

```python
from scripts.main import BankIndustryAnalyzer

analyzer = BankIndustryAnalyzer()

# 获取银行业概览数据
overview = analyzer.get_industry_overview()

# 获取银行业资产质量数据
asset_quality = analyzer.get_asset_quality()

# 获取货币政策数据
policy = analyzer.get_monetary_policy()
```

### CLI命令

```bash
python scripts/main.py --action overview
python scripts/main.py --action asset-quality
python scripts/main.py --action monetary-policy --year 2026
```

## 输出指标说明

| 指标 | 说明 | 数据来源 |
|------|------|----------|
| 银行业总资产 | 银行业金融机构资产合计 | 央行/银保监会 |
| 不良贷款余额 | 次级+可疑+损失类贷款 | 银保监会 |
| 不良贷款率 | 不良贷款余额/贷款余额 | 银保监会 |
| 拨备覆盖率 | 贷款损失准备/不良贷款余额 | 银保监会 |
| 资本充足率 | 资本净额/风险加权资产 | 银保监会 |
| 存款准备金率 | 法定存款准备金率 | 央行 |
| LPR | 贷款市场报价利率 | 央行 |

## 依赖

- akshare >= 1.10.0
- pandas >= 1.3.0
- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
