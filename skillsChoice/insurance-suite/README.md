# 保险套件 (Insurance Suite) - 10个高阶保险Skills

## 概述

保险套件包含10个专业的保险行业分析Skills，覆盖保险市场概览、公司财务分析、寿险/财险业务分析、资金运用、估值分析、偿付能力、政策追踪、国际对比、热点事件等多个维度。使用真实数据源。

---

## 10个Skills一览

| # | Skill名称 | 核心功能 | 数据源 |
|:---:|---|---|---|
| 1 | **insurance-market-overview** | 保险市场概览（保费收入、赔付支出、行业资产） | 金融监管总局、AkShare |
| 2 | **insurance-company-analyzer** | 保险公司分析（财务、偿付能力、业务结构） | AkShare、公司财报 |
| 3 | **insurance-life-analyzer** | 寿险业务分析（新单保费、新业务价值、代理人） | 行业协会、公司年报 |
| 4 | **insurance-pc-analyzer** | 财险业务分析（车险、非车险、综合成本率） | 行业协会、公司财报 |
| 5 | **insurance-investment-analyzer** | 保险资金运用（资产配置、投资收益、利率影响） | 金融监管总局 |
| 6 | **insurance-valuation-analyzer** | 保险股估值分析（PEV、PB、同业对比） | AkShare、公司财报 |
| 7 | **insurance-solvency-analyzer** | 偿付能力分析（充足率、风险评级、监管要求） | 偿付能力报告 |
| 8 | **insurance-policy-tracker** | 政策追踪（监管政策、改革措施、合规动态） | 金融监管总局 |
| 9 | **insurance-sector-comparison** | 行业对比（国内外市场、保险深度/密度） | 瑞士再保险研究所 |
| 10 | **insurance-hot-events** | 热点事件（行业新闻、公司动态、监管处罚） | 行业新闻整理 |

---

## 支持上市保险公司

| 公司 | 代码 | 类型 |
|------|------|------|
| **中国平安** | 601318 | 综合保险 |
| **中国人寿** | 601628 | 寿险 |
| **中国太保** | 601601 | 综合保险 |
| **新华保险** | 601336 | 寿险 |
| **中国人保** | 601319 | 财险 |

---

## 核心业务指标

### 市场指标
| 指标 | 2024年数据 |
|------|------------|
| 保费收入 | 5.7万亿元 |
| 人身险保费 | 3.2万亿元 |
| 财产险保费 | 1.4万亿元 |
| 行业总资产 | 35万亿元 |
| 资金运用余额 | 32万亿元 |

### 经营指标
| 指标 | 说明 | 优秀标准 |
|------|------|----------|
| 综合成本率 | 财险盈利能力 | <100% |
| 新业务价值(NBV) | 寿险增长指标 | 正增长 |
| ROE | 净资产收益率 | >10% |

### 监管指标
| 指标 | 监管要求 |
|------|----------|
| 综合偿付能力充足率 | ≥100% |
| 核心偿付能力充足率 | ≥50% |
| 风险综合评级 | A或B级 |

---

## 使用方法

### 查询市场概览

```bash
cd insurance-market-overview
python scripts/main.py --overview
```

### 分析保险公司

```bash
cd insurance-company-analyzer
python scripts/main.py --company "中国平安"
```

### 寿险业务分析

```bash
cd insurance-life-analyzer
python scripts/main.py --market
```

### 财险业务分析

```bash
cd insurance-pc-analyzer
python scripts/main.py --market
```

### 估值分析

```bash
cd insurance-valuation-analyzer
python scripts/main.py --company "中国平安"
```

### 偿付能力分析

```bash
cd insurance-solvency-analyzer
python scripts/main.py --company "中国平安"
```

---

## 文件结构

```
insurance-suite/
├── README.md
├── insurance-market-overview/
│   ├── SKILL.md
│   ├── LICENSE
│   ├── requirements.txt
│   └── scripts/
│       └── main.py
├── insurance-company-analyzer/
│   └── ...
├── insurance-life-analyzer/
│   └── ...
├── insurance-pc-analyzer/
│   └── ...
├── insurance-investment-analyzer/
│   └── ...
├── insurance-valuation-analyzer/
│   └── ...
├── insurance-solvency-analyzer/
│   └── ...
├── insurance-policy-tracker/
│   └── ...
├── insurance-sector-comparison/
│   └── ...
└── insurance-hot-events/
    └── ...
```

---

## 依赖安装

```bash
# 安装基础依赖
pip install akshare pandas numpy
```

---

## 注意事项

1. **真实数据源**：部分Skills使用AkShare获取实时数据，部分使用最新公开统计数据
2. **数据更新**：行业统计数据通常年度/季度更新
3. **静态数据**：部分政策、行业对比数据使用静态数据，需定期更新

---

## 项目信息

- **开发方**: FinClaw Project
- **许可证**: MIT License
- **创建时间**: 2026-03-22
- **技能数量**: 10个
