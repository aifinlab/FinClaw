<div align="center">
  <div style="font-size: 120px;">🦞</div>
</div>

# FinClaw 🦞 | The First Open-Source Financial Lobster, 1000+ Financial Skills Free for All

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](package.json)
[![Skills](https://img.shields.io/badge/Skills-1000%2B-blueviolet.svg)](#-skills-overview)
[![Free](https://img.shields.io/badge/Free-$0-brightgreen.svg)]()

> **Out-of-the-box financial data research platform** —— **1000+ Financial Skills, 6 Financial Lobsters**, covering **Banking, Securities, Insurance, Funds, Futures, and Trust**, empowering financial professionals across all sectors! **No API Key required, ready to use with one click!**

FinClaw is the first financial lobster launched by Shanghai University of Finance and Economics (SUFE), equipped with 1000+ financial exclusive Skills! As the first open-source system execution framework for the financial industry, FinClaw focuses on deep vertical needs in finance, building "Six Financial Lobsters" around six core sectors: Banking, Securities, Insurance, Funds, Futures, and Trust, each adapted to their unique business processes, regulatory requirements, and delivery scenarios. This framework follows FinEval (China's first financial evaluation system) and Fin-R1 (the first financial reasoning large model) as another open-source contribution from SUFE.

This framework is independently developed by the AIFinLab (Artificial Intelligence Finance Laboratory) team led by Professor Zhang Liwen, Director of the Shanghai Financial Intelligence Engineering Technology Research Center at SUFE School of Statistics and Data Science. The team has long been engaged in the intersection of artificial intelligence, statistics, and finance, with systematic accumulation in scientific research, education integration, industry-academia collaboration, and open-source ecosystem construction, possessing complete technical and engineering capabilities from underlying model R&D to financial scenario implementation and full-stack system building.

[English](README_EN.md) | [中文](README.md)

---

## 💡 Six Financial Lobsters

| Lobster | Positioning | Core Capabilities |
|:---|:---|:---|
| 🦞 **Banking Lobster** | Exclusive advisor for corporate credit & proprietary investment | Credit approval, industry research, asset allocation, credit risk monitoring |
| 🦞 **Fund Lobster** | Precision scalpel for NAV attribution & performance diagnosis | Research backtesting, performance attribution, holding compliance, FOF portfolio construction |
| 🦞 **Securities Lobster** | Precision radar for research judgment & business expansion | Investment banking due diligence, industry research, institutional roadshows, margin trading |
| 🦞 **Insurance Lobster** | Custom expert for liability matching & asset allocation | Product comparison, protection analysis, underwriting & claims, compliance & risk control |
| 🦞 **Trust Lobster** | Exclusive architect for non-standard business & wealth inheritance | Family trust, non-standard valuation, ABS calculation, government credit risk control |
| 🦞 **Futures Lobster** | All-weather trader for market review & trading analysis | Main contract review, cross-period spread, industry-driven analysis |

---

## 🦞 Five Core Advantages

### Addressing Core Pain Points in Daily Financial Work

**1. Deep Financial Industry Adaptation, Breaking Professional Barriers**

Tailored skills for six industries: Banking, Securities, Insurance, Funds, Futures, and Trust. Deeply驯化 and adapted to overcome the professional shortcomings of general AI, providing one-stop solutions for business scenarios across all six sectors.

**2. 1000+ Self-Developed Financial Skills, Covering All Tracks**

From A-share research and quantitative strategies to specialized businesses in banking, insurance, and trust, plus data source integration, compliance auditing, and document processing—covering 20+ major financial scenarios without needing to piece together tools from different sources.

**3. Unified Financial Data Abstraction Layer, Say Goodbye to Data Hunting**

Built-in cn-stock-data unified data entry point with intelligent routing across multiple data sources including AkShare, East Money, Flush, and CNINFO. Unified code format with automatic fallback and fault tolerance—upper-layer applications don't need to worry about data source differences, just use the data directly.

**4. Containerized One-Click Deployment, Enterprise-Grade Security**

Supports Docker containerized one-click deployment, isolating the runtime environment for better data and business security. Easily adaptable to enterprise-grade deployment scenarios.

**5. Native OpenClaw Compatibility, Zero-Barrier One-Click Invocation**

Fully compatible with OpenClaw underlying architecture. No API Key needed, no complex configuration—complete deployment with one command. Directly call the corresponding "lobster" in conversation to complete tasks, seamlessly integrating with general capabilities.

---

## 🎯 60 Featured Financial Skills

Covering six major financial sectors, all using real data sources.

### Banking Suite (10)
| Skill | Description | Data Source |
|:---|:---|:---|
| `bank-industry-analyzer` | Banking industry overview (total assets, net profit, ROE) | PBOC/NAFR |
| `bank-financial-analyzer` | Individual bank financial analysis | Annual reports + Tencent quotes |
| `bank-valuation-analyzer` | Bank valuation analysis (PB/PE/dividend yield) | Real-time quotes + financials |
| `bank-nim-analyzer` | Net Interest Margin (NIM) analysis & comparison | Bank annual reports |
| `bank-risk-analyzer` | Risk indicators (NPL ratio/provision coverage) | Bank annual reports |
| `bank-liquidity-analyzer` | Liquidity indicators (LCR/NSFR) | Bank annual reports |
| `bank-deposit-rates` | Deposit rate query & comparison | Bank official websites + LPR |
| `bank-interbank-market` | Interbank market analysis (Shibor/repo) | Trading center |
| `bank-credit-analyzer` | Credit income/expense analysis | PBOC statistics |
| `bank-wealth-products` | Wealth management product analysis | China Wealth Management Network |

### Securities Suite (10)
| Skill | Description | Data Source |
|:---|:---|:---|
| `securities-industry-analyzer` | Securities industry overview | Securities Association |
| `securities-financial-analyzer` | Broker financial analysis (ROE/leverage) | Annual report data |
| `securities-valuation-analyzer` | Broker valuation analysis | Real-time quotes + financials |
| `securities-brokerage-analyzer` | Brokerage business analysis (volume/market share) | Exchanges |
| `securities-ib-analyzer` | Investment banking analysis (IPO/underwriting) | Securities Association |
| `securities-margin-analyzer` | Margin trading analysis | Shanghai/Shenzhen Exchanges |
| `securities-proprietary-analyzer` | Proprietary trading analysis | Broker annual reports |
| `securities-am-analyzer` | Asset management analysis | AMAC |
| `securities-rating-analyzer` | Broker rating analysis | CSRC classification rating |
| `securities-policy-analyzer` | Industry policy analysis | Regulatory announcements |

### Futures Suite (10)
| Skill | Description | Data Source |
|:---|:---|:---|
| `futures-market-overview` | Futures market overview | Five major exchanges |
| `commodity-futures-analyzer` | Commodity futures analysis (seasonality/basis) | Exchange data |
| `financial-futures-analyzer` | Financial futures analysis (stock index basis) | CFFEX |
| `futures-volume-analyzer` | Volume & open interest analysis | Exchanges |
| `futures-position-tracker` | Position tracking (top traders) | Exchanges |
| `futures-arbitrage-analyzer` | Arbitrage analysis (cross-product/cross-period) | Historical spread statistics |
| `futures-risk-analyzer` | Risk analysis (VaR/volatility) | Historical data |
| `futures-margin-calculator` | Margin calculator | Exchange standards |
| `futures-macro-correlation` | Macro correlation analysis | Historical statistics |
| `futures-delivery-analyzer` | Delivery analysis | Contract information |

### Insurance Suite (10)
| Skill | Description | Data Source |
|:---|:---|:---|
| `insurance-market-overview` | Insurance market overview | NAFR |
| `insurance-company-analyzer` | Insurance company analysis | Company annual reports |
| `insurance-life-analyzer` | Life insurance analysis (NBV/agents) | Company annual reports |
| `insurance-pc-analyzer` | P&C insurance analysis (combined ratio) | Company annual reports |
| `insurance-investment-analyzer` | Investment asset allocation analysis | Company annual reports |
| `insurance-valuation-analyzer` | Insurance valuation (PEV/embedded value) | Real-time quotes + actuarial |
| `insurance-solvency-analyzer` | Solvency analysis | Solvency reports |
| `insurance-policy-tracker` | Policy tracking analysis | Company announcements |
| `insurance-sector-comparison` | Sector comparison analysis | Industry statistics |
| `insurance-hot-events` | Hot events analysis | News sentiment |

### Fund Suite (10)
| Skill | Description | Data Source |
|:---|:---|:---|
| `fund-market-research` | Fund market research | AMAC/third-party |
| `fund-screener` | Fund screener | Multi-source data |
| `fund-risk-analyzer` | Fund risk analysis (VaR/max drawdown) | Historical NAV |
| `fund-portfolio-allocation` | Asset allocation (SAA/TAA/Markowitz) | Multi-source data |
| `fund-sip-planner` | SIP planning/smart SIP | Historical data |
| `fund-rebalance-advisor` | Rebalancing advisor | Holding data |
| `fund-attribution-analysis` | Attribution analysis (Brinson/factor) | Holdings + returns |
| `fund-holding-analyzer` | Holding穿透 analysis | Holding data |
| `fund-tax-optimizer` | Tax optimization (redemption/tax-loss harvesting) | Trading records |
| `fund-monitor` | Fund monitoring & alerts | Real-time data |

### Trust Suite (10)
| Skill | Description | Data Source |
|:---|:---|:---|
| `trust-market-research` | Trust market research | Use Trust/Association |
| `trust-product-analyzer` | Trust product analysis | Product announcements |
| `trust-risk-manager` | Trust risk management | Multi-dimensional assessment |
| `trust-compliance-checker` | Compliance review | Regulatory rules |
| `trust-income-calculator` | Income calculation (IRR/XIRR) | Cash flow |
| `family-trust-designer` | Family trust design | Rule engine |
| `charity-trust-manager` | Charity trust management | Charity data |
| `trust-valuation-engine` | Valuation engine | Multiple valuation methods |
| `trust-post-investment-monitor` | Post-investment monitoring | Project data |
| `trust-asset-allocation` | Asset allocation optimization | Optimization algorithms |

---

## 🌟 Core Highlights

### 1000+ Skills Full Coverage

| Category | Count | Coverage |
|:---|:---:|:---|
| 🏦 **Banking** | 155 | Corporate/Retail/Wealth Management/Risk/Compliance |
| 💼 **Research Assistant** | 357 | Company/Industry Research/Announcement Analysis/DD |
| 📊 **A-Share Research** | 174 | Valuation/Financials/Technical/Fundamentals/Macro |
| 🛡️ **Insurance** | 87 | Underwriting/Claims/Products/Protection/Marketing |
| 📈 **Funds** | 42 | Screening/Allocation/SIP/Attribution/Monitoring |
| 📉 **Securities** | 20 | Brokerage/IB/Asset Management/Margin Trading |
| 🏛️ **Trust** | 20 | Product Analysis/Family Trust/Post-Investment |
| 🗄️ **Data Sources** | 60 | AkShare/Flush/East Money/CNINFO/FRED etc. |
| ⚠️ **Risk & Compliance** | 33 | Compliance checks/Risk alerts/Regulatory reporting |
| 🧰 **General Tools** | 54 | Document processing/Frontend/Skill creation |
| 📰 **News & Sentiment** | 8 | Financial news/Sentiment analysis/Monitoring |
| 🤖 **Quant Tools** | 8 | Backtesting/Factors/Portfolio optimization |
| 📎 **Others** | 7 | AI stock picking/Commodities/Atomic tasks |

**Completely Free · No Registration · Ready to Use**

---

## 🏗️ Technical Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  ① Interface  │  Feishu / Discord / WeChat / CLI                  │
├──────────────────────────────────────────────────────────────────┤
│  ② OpenClaw   │  Message routing / Session mgmt / Skill registry  │
├──────────────────────────────────────────────────────────────────┤
│  ③ FinClaw    │  SOUL personality / Intent / Skill orchestration  │
├──────────────────────────────────────────────────────────────────┤
│  ④ Data Layer │  Unified interface / Multi-source / Fallback      │
├──────────────────────────────────────────────────────────────────┤
│  ⑤ Infra      │  LLM services / File storage / Logging            │
└──────────────────────────────────────────────────────────────────┘
```

**Data Flow**: User Input → Intent Recognition → Skill Orchestration → Multi-source Data Fetch → Formatted Output

---

## 🚀 Quick Start

```bash
# 1. Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. Clone FinClaw
cd ~/.openclaw/workspace
git clone https://github.com/aifinlab/FinClaw .

# 3. Install dependencies
pip install akshare pandas numpy requests

# 4. Start
openclaw start
```

**Usage Examples**:
- "Query Kweichow Moutai stock price"
- "Help me do a DCF valuation for Kweichow Moutai"
- "Analyze recent northbound capital flow"

---

## 📁 Project Structure

```
FinClaw/
├── skills/              # 1000+ complete Skills directory
├── skillschoice/        # 60 featured financial Skills (6 suites)
│   ├── bank-suite/      # Banking suite (10)
│   ├── securities-suite/# Securities suite (10)
│   ├── futures-suite/   # Futures suite (10)
│   ├── insurance-suite/ # Insurance suite (10)
│   ├── fund-suite/      # Fund suite (10)
│   └── trust-suite/     # Trust suite (10)
├── README.md            # This document
└── LICENSE              # Apache 2.0
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|:---|:---|
| OpenClaw not installed | `curl -fsSL https://openclaw.ai/install.sh \| bash` |
| Python dependencies missing | `pip install akshare pandas requests` |
| Skills not found | Check path: `~/.openclaw/workspace/FinClaw/skills` |

---

## 📅 Roadmap

- ✅ **Completed**: 1000+ Skills, unified data abstraction layer, Docker deployment, 60 featured Skills
- 🚧 **In Progress**: Web visualization interface, FinSkillsHub

---

## 🤝 Contributing

Issues and PRs welcome!

```bash
git checkout -b feature/your-feature
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

---

## 📫 Contact Us

We sincerely invite industry peers to explore the innovative paradigm of deep integration of AI and finance, and to build a smart finance ecosystem together.

📧 [zhang.liwen@shufe.edu.cn](mailto:zhang.liwen@shufe.edu.cn)
📧 [chengdongpo@mail.sufe.edu.cn](mailto:chengdongpo@mail.sufe.edu.cn)

---

## 📄 License

[Apache 2.0](LICENSE) © 2026 FinClaw Contributors
