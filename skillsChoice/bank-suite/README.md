# 银行套件 (Bank Suite) - 10个高阶银行Skills

## 概述

银行套件包含10个专业的银行分析Skills，覆盖银行业宏观分析、个体银行财务分析、风险分析、流动性分析、估值分析等多个维度。全部使用真实数据源，包括AkShare、Tushare、同花顺API、央行和银保监会官方数据。

---

## 10个Skills一览

| # | Skill名称 | 核心功能 | 数据源 |
|:---:|---|---|---|
| 1 | **bank-industry-analyzer** | 银行业宏观分析（资产规模、存贷款、利润、资产质量） | AkShare、央行、银保监会 |
| 2 | **bank-financial-analyzer** | 商业银行财务深度分析（ROE、ROA、三大表） | 同花顺、Tushare、AkShare |
| 3 | **bank-risk-analyzer** | 银行风险分析（不良率、拨备覆盖率、资本充足率） | AkShare、Tushare |
| 4 | **bank-liquidity-analyzer** | 银行流动性分析（LCR、NSFR、存贷比） | AkShare、央行 |
| 5 | **bank-valuation-analyzer** | 银行股估值分析（PB、PE、股息率、同业对比） | 同花顺、AkShare |
| 6 | **bank-deposit-rates** | 银行存款利率查询与对比（各期限挂牌利率） | 各银行官网、央行 |
| 7 | **bank-wealth-products** | 银行理财产品分析（收益率、风险等级筛选） | 中国理财网、AkShare |
| 8 | **bank-interbank-market** | 银行间市场分析（Shibor、回购利率、流动性） | 中国货币网、AkShare |
| 9 | **bank-nim-analyzer** | 银行净息差分析（NIM、生息资产收益率、负债成本） | Tushare、AkShare |
| 10 | **bank-credit-analyzer** | 银行信贷结构分析（对公/零售/票据、行业投向） | 央行、AkShare |

---

## 数据源详情

### 主要数据源

| 数据源 | 数据类型 | 覆盖范围 |
|--------|----------|----------|
| **AkShare** | 实时行情、财报数据、宏观指标 | A股上市银行、行业统计 |
| **Tushare Pro** | 详细三大表、财务指标 | 42家上市银行 |
| **同花顺iFinD API** | 实时行情、估值指标 | 全市场银行股 |
| **中国人民银行** | 货币政策、LPR、准备金率、信贷数据 | 全国金融数据 |
| **国家金融监督管理总局** | 监管指标、行业统计数据 | 银行业监管数据 |
| **中国理财网** | 理财产品发行数据 | 全市场理财产品 |
| **中国货币网** | Shibor、回购利率 | 银行间市场数据 |
| **各银行官网** | 存款利率、理财产品 | 各银行挂牌利率 |

---

## 使用示例

### 1. 分析单家银行

```bash
# 分析招商银行财务
cd bank-financial-analyzer
python scripts/main.py --bank "招商银行" --action analyze

# 分析工商银行风险指标
cd bank-risk-analyzer
python scripts/main.py --bank "工商银行" --action analyze
```

### 2. 对比多家银行

```bash
# 对比NIM
cd bank-nim-analyzer
python scripts/main.py --compare

# 对比估值
cd bank-valuation-analyzer
python scripts/main.py --compare
```

### 3. 查询市场数据

```bash
# 查询Shibor
cd bank-interbank-market
python scripts/main.py --shibor

# 查询存款利率
cd bank-deposit-rates
python scripts/main.py --compare "3年"
```

---

## 支持的上市银行

### 国有大行（6家）
工商银行、农业银行、中国银行、建设银行、交通银行、邮储银行

### 股份制银行（9家）
招商银行、兴业银行、浦发银行、中信银行、民生银行、光大银行、平安银行、华夏银行、浙商银行

### 主要城商行
北京银行、上海银行、江苏银行、南京银行、宁波银行、杭州银行、成都银行、长沙银行等

---

## 核心指标说明

### 盈利能力指标
| 指标 | 优秀 | 良好 | 一般 |
|------|------|------|------|
| ROE | ≥15% | 10-15% | <10% |
| ROA | ≥1% | 0.8-1% | <0.8% |
| NIM | ≥2.5% | 2.0-2.5% | <2.0% |

### 风险指标
| 指标 | 监管要求 | 优秀 |
|------|----------|------|
| 不良贷款率 | <5% | <1% |
| 拨备覆盖率 | ≥150% | ≥300% |
| 资本充足率 | ≥10.5% | ≥13% |

### 估值指标
| 指标 | 低估 | 合理 | 溢价 |
|------|------|------|------|
| PB | <0.8 | 0.8-1.2 | >1.2 |
| PE | <6 | 6-10 | >10 |
| 股息率 | >5% | 3-5% | <3% |

---

## 文件结构

```
bank-suite/
├── bank-industry-analyzer/
│   ├── SKILL.md
│   ├── LICENSE
│   ├── requirements.txt
│   └── scripts/
│       └── main.py
├── bank-financial-analyzer/
│   └── ...
├── bank-risk-analyzer/
│   └── ...
├── bank-liquidity-analyzer/
│   └── ...
├── bank-valuation-analyzer/
│   └── ...
├── bank-deposit-rates/
│   └── ...
├── bank-wealth-products/
│   └── ...
├── bank-interbank-market/
│   └── ...
├── bank-nim-analyzer/
│   └── ...
└── bank-credit-analyzer/
    └── ...
```

---

## 依赖安装

```bash
# 安装基础依赖
pip install akshare pandas numpy requests beautifulsoup4 lxml

# 安装Tushare Pro（需注册获取token）
pip install tushare

# 设置环境变量
export TUSHARE_TOKEN="your_token_here"
export THS_ACCESS_TOKEN="your_ths_token_here"
```

---

## 注意事项

1. **真实数据源**：所有Skills均使用真实数据源，非模拟数据
2. **API限制**：部分数据源有调用频率限制，请合理使用
3. **数据更新**：财务数据通常季度更新，行情数据实时更新
4. **环境变量**：Tushare和同花顺API需要配置token

---

## 项目信息

- **开发方**: FinClaw Project
- **许可证**: MIT License
- **创建时间**: 2026-03-22
- **技能数量**: 10个
