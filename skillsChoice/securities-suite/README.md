# 证券套件 (Securities Suite) - 10个高阶证券Skills

## 概述

证券套件包含10个专业的证券行业分析Skills，覆盖证券行业宏观分析、券商财务分析、各业务条线分析（投行/经纪/资管/自营/两融）、估值分析、评级分析、政策分析等多个维度。全部使用真实数据源。

---

## 10个Skills一览

| # | Skill名称 | 核心功能 | 数据源 |
|:---:|---|---|---|
| 1 | **securities-industry-analyzer** | 证券行业宏观分析（规模、结构、集中度） | AkShare、中证协、证监会 |
| 2 | **securities-financial-analyzer** | 券商财务深度分析（ROE、杠杆率、收入结构） | 同花顺、Tushare、AkShare |
| 3 | **securities-valuation-analyzer** | 券商股估值分析（PB、PE、同业对比） | 同花顺、AkShare |
| 4 | **securities-ib-analyzer** | 投行业务分析（IPO、再融资、债券承销） | 证监会、交易所、AkShare |
| 5 | **securities-brokerage-analyzer** | 经纪业务分析（成交额、佣金率、市占率） | 交易所、中证协、AkShare |
| 6 | **securities-am-analyzer** | 资管业务分析（规模、排名、产品结构） | 中基协、中证协、AkShare |
| 7 | **securities-proprietary-analyzer** | 自营业务分析（投资收益、收益率、持仓） | Tushare、AkShare |
| 8 | **securities-margin-analyzer** | 两融业务分析（余额、维保比例、趋势） | 交易所、AkShare |
| 9 | **securities-rating-analyzer** | 券商评级分析（证监会分类评级、业务资格） | 证监会、中证协 |
| 10 | **securities-policy-analyzer** | 证券行业政策分析（监管政策、创新业务） | 证监会、交易所、AkShare |

---

## 数据源详情

| 数据源 | 数据类型 | 覆盖范围 |
|--------|----------|----------|
| **AkShare** | 实时行情、财报数据、新股数据、两融数据 | 全部上市券商 |
| **Tushare Pro** | 详细三大表、财务指标 | 50+家上市券商 |
| **同花顺iFinD API** | 实时行情、估值指标 | 全市场券商股 |
| **中国证监会** | 监管政策、券商评级、处罚信息 | 全行业 |
| **中国证券业协会** | 行业统计数据、排名 | 全行业 |
| **中国证券投资基金业协会** | 资管业务数据 | 券商资管 |
| **沪深交易所** | 成交额、IPO数据、两融数据 | 全市场 |
| **巨潮资讯网** | 新股数据、处罚信息 | 全市场 |

---

## 支持的上市券商

### 头部券商（10家）
中信证券、华泰证券、海通证券、国泰君安、招商证券、广发证券、中国银河、中信建投、中金公司、东方证券

### 中型券商（20+家）
兴业证券、光大证券、国信证券、申万宏源、东方财富、浙商证券、方正证券、国金证券、东吴证券、财通证券、长城证券、国联证券、南京证券、红塔证券、中银证券、华安证券、山西证券、西部证券、第一创业、西南证券、国海证券等

---

## 核心指标说明

### 盈利能力指标
| 指标 | 优秀 | 良好 | 一般 |
|------|------|------|------|
| ROE | ≥8% | 5-8% | <5% |
| 杠杆率 | 3-5x | 2-3x或5-6x | <2x或>6x |

### 估值指标
| 指标 | 低估 | 合理 | 溢价 |
|------|------|------|------|
| PB | <1.2 | 1.2-2.0 | >2.0 |
| PE | <15 | 15-25 | >25 |

### 业务指标
| 业务 | 核心指标 | 头部标准 |
|------|----------|----------|
| 投行 | 承销规模市占率 | >5% |
| 经纪 | 股基成交额市占率 | >4% |
| 资管 | 主动管理规模 | 行业前10 |
| 自营 | 投资收益率 | >5% |

---

## 使用方法

### 分析单家券商

```bash
# 分析中信证券财务
cd securities-financial-analyzer
python scripts/main.py --securities "中信证券" --action analyze

# 分析华泰证券估值
cd securities-valuation-analyzer
python scripts/main.py --securities "华泰证券"
```

### 对比多家券商

```bash
# 对比自营业务
cd securities-proprietary-analyzer
python scripts/main.py --compare

# 对比估值
cd securities-valuation-analyzer
python scripts/main.py --compare
```

### 查询市场数据

```bash
# 查询IPO数据
cd securities-ib-analyzer
python scripts/main.py --ipo --year 2026

# 查询两融数据
cd securities-margin-analyzer
python scripts/main.py --overview

# 查询最新政策
cd securities-policy-analyzer
python scripts/main.py --policies
```

---

## 文件结构

```
securities-suite/
├── README.md
├── securities-industry-analyzer/
│   ├── SKILL.md
│   ├── LICENSE
│   ├── requirements.txt
│   └── scripts/
│       └── main.py
├── securities-financial-analyzer/
│   └── ...
├── securities-valuation-analyzer/
│   └── ...
├── securities-ib-analyzer/
│   └── ...
├── securities-brokerage-analyzer/
│   └── ...
├── securities-am-analyzer/
│   └── ...
├── securities-proprietary-analyzer/
│   └── ...
├── securities-margin-analyzer/
│   └── ...
├── securities-rating-analyzer/
│   └── ...
└── securities-policy-analyzer/
    └── ...
```

---

## 依赖安装

```bash
# 安装基础依赖
pip install akshare pandas numpy requests

# 安装Tushare Pro（需注册获取token）
pip install tushare

# 设置环境变量
export TUSHARE_TOKEN="your_token_here"
export THS_ACCESS_TOKEN="your_ths_token_here"
```

---

## 注意事项

1. **真实数据源**：所有Skills均使用真实数据源
2. **API限制**：部分数据源有调用频率限制
3. **数据更新**：财务数据通常季度更新，行情数据实时更新
4. **环境变量**：Tushare和同花顺API需要配置token

---

## 项目信息

- **开发方**: FinClaw Project
- **许可证**: MIT License
- **创建时间**: 2026-03-22
- **技能数量**: 10个
