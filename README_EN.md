<div align="center">
  <img src="images/finclaw-logo.png" alt="finclaw-logo" width="300">
</div>

# FinClaw 🦞 | The First Open-Source Finance-Dedicated Lobster, 1000+ Financial Skills Fully Free

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](package.json)
[![Skills](https://img.shields.io/badge/Skills-1000+%2B-blueviolet.svg)](#-core-highlights-of-finclaw)
[![Free](https://img.shields.io/badge/Free-$0-brightgreen.svg)]()

> **A ready-to-use financial data and investment research powerhouse — featuring 60 carefully selected core financial Skills, 1000+ open-source Skills, and 6 financial lobsters covering banking, securities, insurance, funds, futures, and trusts. Empowering finance professionals across every major track. No API Key required. Get started with one click!**

[English](README_EN.md) | [中文](README.md)

---

**FinClaw** is the first open-source execution framework built specifically for the financial industry. It is jointly developed by the Artificial Intelligence Finance Laboratory (AIFinLab), led by **Professor Liwen Zhang, Director of the Shanghai Financial Intelligence Engineering Technology Research Center and faculty member at the School of Statistics and Data Science, Shanghai University of Finance and Economics**. FinClaw is not a generic, all-purpose agent. Instead, it is **six specialized lobsters, each vertically tailored to a specific segment of the financial industry**. Banking, securities, funds, insurance, futures, and trusts — each of these six sectors has its own business processes, regulatory logic, and delivery scenarios, and each deserves a lobster that truly understands the field.

## 💡 Use Cases

### 🦞 **Banking Lobster | Dedicated Think Tank for Corporate Credit + Proprietary Investment**
FinClaw’s Banking Lobster can rapidly generate professional outputs for core scenarios such as credit approval, industry research, and asset allocation, including industry credit risk monitoring lists and strategic asset allocation ideas for proprietary accounts. It helps front-load a large amount of repetitive preliminary analysis work.


https://github.com/user-attachments/assets/1db084f2-1cd4-417d-989a-636ea281cd1e


### 🦞 **Securities Lobster | Precision Radar for Investment Research + Business Expansion**
FinClaw’s Securities Lobster can accurately capture policy signals and market themes across workflows ranging from investment banking due diligence materials and industry research coverage prioritization to key institutional roadshow topics and margin financing/securities lending analysis, helping both research and brokerage businesses stay in sync with the market rhythm.


https://github.com/user-attachments/assets/bf20305f-1bb4-4ced-b63b-c9f7f3710d0d


### 🦞 **Insurance Lobster | Customized Expert for Liability Matching + Asset Allocation**
FinClaw’s Insurance Lobster can generate asset allocation strategies better aligned with real insurance business scenarios by incorporating insurers’ liability structures, interest-rate environments, and risk preferences. It also covers common tasks such as product comparison, protection analysis, underwriting and claims, compliance, and risk control.



https://github.com/user-attachments/assets/0ef1dba7-11f4-4bc0-938e-cd0b998e91d0



### 🦞 **Fund Lobster | Precision Scalpel for NAV Attribution + Performance Diagnosis**
FinClaw’s Fund Lobster can identify the core reasons why an ETF underperformed its benchmark with one click, locate heavyweight holdings dragging down NAV, distinguish between fundamental, trading, and event-driven impacts, and cover the full workflow from investment research backtesting and performance attribution to holding compliance and FOF portfolio construction.


https://github.com/user-attachments/assets/b0c9f07b-355d-48b5-9809-4700c92bb79c


### 🦞 **Futures Lobster | Around-the-Clock Trader for Market Replay + Trading Analysis**
FinClaw’s Futures Lobster can complete main contract reviews in minutes, break down intraday turning points, volume/open-interest changes, calendar spreads, and industrial drivers, and accurately assess whether late-session volatility reflects trend continuation, emotional release, or short-term overselling. Both quantitative and discretionary traders can use it out of the box.



https://github.com/user-attachments/assets/b71a3f66-3faa-482b-8098-313fd34dc3b9



### 🦞 **Trust Lobster | Dedicated Architect for Non-Standard Business + Wealth Inheritance**
FinClaw’s Trust Lobster can generate asset suitability diagnostics, risk identification, beneficiary distribution frameworks, and control-right arrangement suggestions for scenarios such as family trusts, HNW client services, non-standard asset valuation, ABS analysis, and government-financing risk control, supporting more complete solution design.



https://github.com/user-attachments/assets/773affad-4b35-4ded-a39d-7ada54071719




---

## 🌟 Core Highlights of FinClaw

FinClaw centers on a full closed loop for financial business workflows, forming a complete chain from underlying data to upper-layer applications. The system adopts a layered architecture that decouples and reconstructs financial capabilities and task execution. At the bottom layer, a Skills library accumulates standardized financial task capabilities. At the top layer, a unified task orchestration and scheduling mechanism dynamically combines and invokes these capabilities, enabling a leap from mere “tool calling” to true “task execution.”

### 1️⃣ 60 Carefully Selected In-House Financial Skills That Break Through Professional Barriers

Tailored to the characteristics of the six major financial industries — banking, securities, funds, insurance, futures, and trusts — FinClaw selectively curates and deeply adapts high-frequency business capabilities to fill the gap left by general AI in professional scenarios. Based on typical financial business workflows, related capabilities are abstracted and structured into standardized, reusable modules, building a high-quality and reusable Skills capability set that supports the entire pipeline from data acquisition and processing to analysis and result output. The capability system is uniformly connected to multiple real-world data sources to ensure stability, consistency, and professionalism during task execution.

#### Banking Suite (10 Skills)

| Skill | Description | Data Source |
|:---|:---|:---|
| `bank-industry-analyzer` | Banking industry overview analysis (total assets, net profit, ROE) | PBOC / NFRA |
| `bank-financial-analyzer` | Single-bank financial analysis | Annual reports + Tencent market data |
| `bank-valuation-analyzer` | Bank valuation analysis (PB/PE/dividend yield) | Real-time market data + financials |
| `bank-nim-analyzer` | Net interest margin (NIM) comparative analysis | Bank annual reports |
| `bank-risk-analyzer` | Risk metrics analysis (NPL ratio / provision coverage) | Bank annual reports |
| `bank-liquidity-analyzer` | Liquidity metrics analysis (LCR / NSFR) | Bank annual reports |
| `bank-deposit-rates` | Deposit rate query and comparison | Bank websites + LPR |
| `bank-interbank-market` | Interbank market analysis (Shibor / repo) | Trading center |
| `bank-credit-analyzer` | Credit balance analysis | PBOC statistics |
| `bank-wealth-products` | Wealth management product analysis | China Wealth Management Net |

#### Securities Suite (10 Skills)

| Skill | Description | Data Source |
|:---|:---|:---|
| `securities-industry-analyzer` | Securities industry overview analysis | Securities Association of China |
| `securities-financial-analyzer` | Broker financial analysis (ROE / leverage ratio) | Annual report data |
| `securities-valuation-analyzer` | Broker valuation analysis | Real-time market data + financials |
| `securities-brokerage-analyzer` | Brokerage business analysis (trading volume / market share) | Exchanges |
| `securities-ib-analyzer` | Investment banking business analysis (IPO / underwriting) | Securities Association of China |
| `securities-margin-analyzer` | Margin trading and securities lending analysis | SSE / SZSE |
| `securities-proprietary-analyzer` | Proprietary trading business analysis | Broker annual reports |
| `securities-am-analyzer` | Asset management business analysis | AMAC |
| `securities-rating-analyzer` | Broker rating analysis | CSRC classification evaluations |
| `securities-policy-analyzer` | Industry policy analysis | Regulatory announcements |

#### Futures Suite (10 Skills)

| Skill | Description | Data Source |
|:---|:---|:---|
| `futures-market-overview` | Futures market overview | Five major exchanges |
| `commodity-futures-analyzer` | Commodity futures analysis (seasonality / basis) | Exchange data |
| `financial-futures-analyzer` | Financial futures analysis (stock index futures basis) | CFFEX |
| `futures-volume-analyzer` | Volume and open interest analysis | Exchanges |
| `futures-position-tracker` | Position tracking (top traders list) | Exchanges |
| `futures-arbitrage-analyzer` | Arbitrage analysis (cross-product / calendar spread) | Historical spread statistics |
| `futures-risk-analyzer` | Risk analysis (VaR / volatility) | Historical data |
| `futures-margin-calculator` | Margin calculator | Exchange standards |
| `futures-macro-correlation` | Macro correlation analysis | Historical statistics |
| `futures-delivery-analyzer` | Delivery analysis | Contract information |

#### Insurance Suite (10 Skills)

| Skill | Description | Data Source |
|:---|:---|:---|
| `insurance-market-overview` | Insurance market overview | NFRA |
| `insurance-company-analyzer` | Insurance company analysis | Company annual reports |
| `insurance-life-analyzer` | Life insurance business analysis (NBV / agents) | Company annual reports |
| `insurance-pc-analyzer` | Property & casualty insurance business analysis (combined ratio) | Company annual reports |
| `insurance-investment-analyzer` | Investment asset allocation analysis | Company annual reports |
| `insurance-valuation-analyzer` | Insurance valuation (PEV / embedded value) | Real-time market data + actuarial data |
| `insurance-solvency-analyzer` | Solvency analysis | Solvency reports |
| `insurance-policy-tracker` | Policy tracking analysis | Company announcements |
| `insurance-sector-comparison` | Industry comparison analysis | Industry statistics |
| `insurance-hot-events` | Hot-topic event analysis | News and public opinion |

#### Fund Suite (10 Skills)

| Skill | Description | Data Source |
|:---|:---|:---|
| `fund-market-research` | Fund market research | AMAC / third-party sources |
| `fund-screener` | Fund screener | Multi-source data |
| `fund-risk-analyzer` | Fund risk analysis (VaR / max drawdown) | Historical NAV |
| `fund-portfolio-allocation` | Asset allocation (SAA / TAA / Markowitz) | Multi-source data |
| `fund-sip-planner` | SIP planning / smart DCA | Historical data |
| `fund-rebalance-advisor` | Rebalancing advisor | Holding data |
| `fund-attribution-analysis` | Attribution analysis (Brinson / factor) | Holdings + returns |
| `fund-holding-analyzer` | Look-through holding analysis | Holding data |
| `fund-tax-optimizer` | Tax optimization (redemption / tax-loss harvesting) | Trading records |
| `fund-monitor` | Fund monitoring and alerting | Real-time data |

#### Trust Suite (10 Skills)

| Skill | Description | Data Source |
|:---|:---|:---|
| `trust-market-research` | Trust market research | Use Trust / associations |
| `trust-product-analyzer` | Trust product analysis | Product announcements |
| `trust-risk-manager` | Trust risk management | Multi-dimensional evaluation |
| `trust-compliance-checker` | Compliance review | Regulatory rules |
| `trust-income-calculator` | Return calculator (IRR / XIRR) | Cash flow |
| `family-trust-designer` | Family trust design | Rule engine |
| `charity-trust-manager` | Charity trust management | Public welfare data |
| `trust-valuation-engine` | Valuation engine | Multi-method valuation |
| `trust-post-investment-monitor` | Post-investment monitoring | Project data |
| `trust-asset-allocation` | Asset allocation optimization | Optimization algorithms |

### 2️⃣ 1000+ In-House Financial Skills

FinClaw’s Skills system is not simply divided by financial sectors. Instead, it starts from a deeper capability structure and abstracts the common capabilities across financial business scenarios into standardized modules. In practical use, these capabilities can be flexibly orchestrated and combined, thereby naturally extending into six core financial application scenarios: banking, securities, funds, insurance, futures, and trusts.

| Category | Count | Coverage |
|:---|:---:|:---|
| 🏦 Banking | 155 | Corporate / retail / wealth management / risk management / compliance operations |
| 💼 Investment Research Assistant | 357 | Company research / industry research / announcement analysis / due diligence |
| 📊 A-Share Research | 174 | Valuation / financial reports / technicals / capital flows / sentiment / macro / stock selection |
| 🛡️ Insurance | 87 | Underwriting / claims / products / protection / marketing / compliance |
| 📈 Funds | 42 | Screening / allocation / SIP / attribution / monitoring |
| 📉 Securities | 20 | Brokerage / investment banking / asset management / margin financing |
| 🏛️ Trusts | 20 | Product analysis / family trusts / post-investment monitoring |
| 🗄️ Data Sources | 60 | AkShare / Tonghuashun / Eastmoney / CNINFO / FRED, etc. |
| ⚠️ Risk Control & Compliance | 33 | Compliance checks / risk alerts / regulatory reporting |
| 🧰 General Tools | 54 | Document processing / frontend design / skill creation |
| 📰 News & Sentiment | 8 | Financial news / sentiment analysis / public opinion monitoring |
| 🤖 Quant Tools | 8 | Backtesting / factors / portfolio optimization / visualization |
| 📎 Others | 7 | AI stock selection / commodity data / atomic tasks |

**Completely free · No registration required · Install and use immediately**

### 3️⃣ Unified Financial Data Abstraction Layer

FinClaw builds a standardized data access layer by wrapping multi-source financial data interfaces based on cn-stock-data, enabling a unified schema, code format, and access protocol across data sources. Through intelligent routing and fault-tolerant degradation, the system dynamically dispatches between sources such as AkShare, Eastmoney, Tonghuashun, and CNINFO, shielding upper layers from source-level differences while ensuring service stability. This allows upper-layer Agents and Skills to invoke data through a consistent interface.

```text
User Request → cn-stock-data (Unified Entry) → Intelligent Routing → efinance / akshare / adata / ashare / snowball
```

| Data Type | Routing Priority |
|:---|:---|
| K-line market data | efinance → akshare → adata → ashare → snowball |
| Real-time quotes | efinance → adata → snowball |
| Financial indicators | adata → akshare → snowball |
| Northbound capital | adata exclusive |
| Cross-market data | snowball exclusive |

**Unified code format (SH600519), unified field names (English snake_case), and automatic fallback — upper-layer Skills do not need to care about data source differences.**

### 4️⃣ One-Click Containerized Deployment

In addition to supporting standardized local installation, FinClaw provides a Docker-based containerized deployment solution that packages the runtime environment, dependencies, and core services into a unified bundle for out-of-the-box startup. Container isolation effectively avoids environment conflicts, improves system stability and reproducibility, and offers stronger protection at both the data and business levels. At the same time, this approach has strong scalability and environment adaptability, making it suitable for seamless enterprise deployment and production use.

**Standard Installation (Recommended)**

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

**Docker Deployment**
```
# 1. Start the OpenClaw container
docker run -d --name openclaw -p 18789:18789 openclaw/openclaw:latest

# 2. Copy FinClaw into the container
docker exec openclaw mkdir /home/node/.openclaw/workspace/
docker cp ./FinClaw openclaw:/home/node/.openclaw/workspace/FinClaw

# 3. Restart the container
docker restart openclaw
```

---

### 5️⃣ Zero-Barrier Task Execution Capability
FinClaw is natively compatible with the OpenClaw Agent OS architecture and can seamlessly integrate with its message routing, session management, skill registration, and permission control system. The system requires no additional API Key or complex environment configuration. Deployment can be completed through a standardized startup process, delivering out-of-the-box financial task execution capability. Users can directly invoke the corresponding financial Skills in a conversational environment and orchestrate them together with general-purpose capabilities.
**Method 1: Invoke via OpenClaw Agent (Recommended)**
After startup, interact directly with OpenClaw in conversation, for example:
- "Check the stock price trend of Kweichow Moutai"
- "Help me do a DCF valuation for Kweichow Moutai"
- ""Analyze recent northbound capital movements"
- "Backtest a momentum strategy on CSI 300 constituents"
**Method 2: Run Skills directly from the command line**
```
# View all skills
ls -1 skills/

# Find by category
ls -1 skills/ | grep "^bank-"        # Banking
ls -1 skills/ | grep "^a-share-"     # A-share related
ls -1 skills/ | grep "^fund-"        # Funds
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|:---|:---|
| OpenClaw not installed | `curl -fsSL https://openclaw.ai/install.sh` |
| Missing Python dependencies | `pip install akshare pandas requests` |
| Skills not found | Confirm path: `~/.openclaw/workspace/FinClaw/skills` |

### Check installation status

```bash
# Check whether OpenClaw is installed
openclaw version

# Check whether skills are correctly placed
openclaw config get skills.load.extraDirs

# Check Python dependencies
python -c "import akshare; print(akshare.__version__)"
```

---

## 📅 Roadmap

- ✅ **Completed**：1000+ Skills, unified data abstraction layer, Docker deployment, 60 curated Skills
- 🚧 **In Progress**：Web visualization interface, FinSkillsHub

---

## 🤝 Contributing

Issues and PRs are welcome!

```bash
git checkout -b feature/your-feature
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

---

## 📫 Contact Us

We sincerely invite industry peers to explore innovative paradigms for the deep integration of AI and finance and to jointly build a new ecosystem for intelligent finance. Feel free to contact us by email:
📧 [zhang.liwen@shufe.edu.cn](mailto:zhang.liwen@shufe.edu.cn)
📧 [chengdongpo@mail.sufe.edu.cn](mailto:chengdongpo@mail.sufe.edu.cn)

👉If you would like to engage in deeper discussions on project co-construction, scientific research, talent cultivation, or industrial applications, please scan the QR code and fill out the form.
<div align="center">
  <img src="images/contact.png" alt="contact" width="300">
</div>

---

## 📄 If you would like to engage in deeper discussions on project co-construction, scientific research, talent cultivation, or industrial applications, please scan the QR code and fill out the form.

[Apache 2.0](LICENSE) © 2026 FinClaw Contributors

