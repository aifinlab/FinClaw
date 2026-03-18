<div align="center">
  <div style="font-size: 120px;">🦞</div>
</div>

# FinClaw 🦞 | Open-Source Free-to-Use Financial Lobster with 960 Self-Developed Skills

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](package.json)
[![Skills](https://img.shields.io/badge/Skills-960-blueviolet.svg)](#-skills-overview-960)
[![Free](https://img.shields.io/badge/Free-$0-brightgreen.svg)]()

> **Ready-to-Use Financial Data & Research Tool** — **960 Skills** covering A-share research/quant strategies/data sources/insurance/banking/research assistants/general tools. **No API Key Required, One-Click Start!**

[English](README_EN.md) | [中文](README.md)

---

## 🚀 Quick Start

FinClaw is a financial data Skills collection developed based on **OpenClaw**, and must run on OpenClaw.

### Installation & Deployment

**Standard Installation (Recommended)**

```bash
# 1. Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. Navigate to workspace directory
cd ~/.openclaw/workspace

# 3. Clone FinClaw project
git clone https://github.com/aifinlab/FinClaw .

# 4. Install Python dependencies
pip install akshare pandas numpy requests

# 5. Start OpenClaw
openclaw start
```

**Docker Deployment**

```bash
# 1. Start OpenClaw container
docker run -d --name openclaw -p 18789:18789 openclaw/openclaw:latest

# 2. Copy FinClaw to container
docker exec openclaw mkdir /home/node/.openclaw/workspace/
docker cp ./FinClaw openclaw:/home/node/.openclaw/workspace/FinClaw

# 3. Restart container
docker restart openclaw
```

### Usage

**Method 1: OpenClaw Agent (Recommended)**

After startup, interact directly with OpenClaw:
- "Query Moutai stock price"
- "Perform DCF valuation for Kweichow Moutai"
- "Analyze recent northbound capital flows"
- "Backtest CSI 300 constituents with momentum strategy"

**Method 2: Direct CLI Execution**

```bash
# View all skills
ls -1 skills/

# Search by category
ls -1 skills/ | grep "^bank-"        # Banking
ls -1 skills/ | grep "^a-share-"     # A-share
ls -1 skills/ | grep "^fund-"        # Funds
```

---

## 🚀 Four Core Highlights

### 1️⃣ 960 Skills Covering All Categories

| Category | Count | Coverage |
|:---|:---:|:---|
| 🏦 **Banking** | 134 | Corporate/Retail/Wealth/Risk/Compliance/Transaction Banking |
| 💼 **Research & Wealth** | 122 | Research assistants/Wealth management/Client service/Asset allocation |
| 🗄️ **Data Sources** | 60 | Unified abstraction layer + AkShare + Eastmoney/THS/CNINFO/FRED/ECB/BOJ |
| 📑 **Due Diligence** | 57 | DD checklists/Project admission/Entity DD/Ongoing monitoring |
| 🛡️ **Insurance** | 55 | Underwriting/Claims/Product comparison/Coverage analysis/Marketing |
| 📊 **A-share Research** | 54 | Valuation/Financials/Sector/Technical/Capital/Sentiment/Macro |
| 🔢 **A-share Quant** | 50 | Factors/Strategies/Risk/Data mining/Sector quant/Trading signals |
| 🔧 **Data Processing** | 47 | Global retrieval/Data cleaning/Entity recognition/Field mapping |
| 🎯 **Product & Marketing** | 43 | Product management/Marketing opportunities/Sales scripts/Roadshow |
| 📋 **Compliance & Audit** | 37 | Compliance review/Regulatory reporting/Audit trail/Approval process |
| 📈 **Fund Business** | 35 | Fund diagnostics/Holding companion/Announcement interpretation |
| ⚠️ **Risk Management** | 25 | Risk alerts/Risk attribution/Risk reports/Threshold monitoring |
| 🧰 **General Tools** | 24 | MCP/API/Frontend/Document processing/Skill creator |
| 🏛️ **Trust Business** | 20 | Family trust/Trust solutions/Trustee reports/Trust policies |
| 📞 **Operations** | 17 | Meeting minutes/Service process/Operations reports |
| 🚨 **Anomaly Detection** | 16 | Abnormal trading/Account monitoring/Behavior correlation |
| 📄 **Document Processing** | 10 | PDF/Word/Excel/OCR/Table recognition |
| 🤖 **Quant Tools** | 8 | Backtesting/Factors/AI stock picking/Portfolio optimization |
| 📰 **News & Sentiment** | 7 | Financial news/Sentiment analysis/Eastmoney/Weibo/Xueqiu |
| 📎 **Others** | 139 | Various specialized business scenarios and custom solutions |

**All Free** · **No Registration** · **Ready to Use**

---

### 2️⃣ Unified Data Abstraction Layer (cn-stock-data)

```
User Request → cn-stock-data (Unified Entry) → Smart Routing → efinance / akshare / adata / ashare / snowball
```

| Data Type | Routing Priority |
|:---|:---|
| K-line | efinance → akshare → adata → ashare → snowball |
| Real-time Quote | efinance → adata → snowball |
| Capital Flow | efinance → adata → snowball |
| Financial Metrics | adata → akshare → snowball |
| Northbound Capital | adata exclusive |
| Cross-market (HK/US) | snowball exclusive |

**Unified code format (SH600519), unified field names (English snake_case), automatic fallback. Upper-layer Skills don't need to worry about data source differences.**

---
### 3️⃣ Ready to Use — Just One Command
**No API Key, No Configuration, Install and Use!**

---
### 4️⃣ Full-Featured — Complete Research Workflow
| Stage | Coverage |
|:---|:---|
| **Pre-market** | Morning briefing, financial news analysis, earnings preview, macro data interpretation |
| **Intraday** | Northbound capital, main capital, dragon-tiger list, market sentiment, limit tracking |
| **Post-market** | Stock review, weekly review, technical analysis, research digest, event-driven |
| **Deep Research** | DCF valuation, comparable companies, financial health, moat, industry chain, investment thesis |
| **Quant Strategy** | Factor analysis, momentum/mean reversion/trend following/pairs trading, portfolio optimization, risk attribution |
| **Risk Control** | VaR analysis, drawdown analysis, stop-loss strategy, tail risk, position management |


## 🧠 Skills Overview (960)

> **Note**: FinClaw now includes **960 Skills**, distributed as follows:
> - 🏦 Banking 134 | 💼 Research & Wealth 122 | 🗄️ Data Sources 60 | 📑 DD & Projects 57 | 🛡️ Insurance 55
> - 📊 A-share Research 54 | 🔢 A-share Quant 50 | 🔧 Data Processing 47 | 🎯 Product & Marketing 43 | 📋 Compliance 37
> - 📈 Fund Business 35 | ⚠️ Risk Management 25 | 🧰 General Tools 24 | 🏛️ Trust 20 | 📞 Operations 17
> - 🚨 Anomaly Detection 16 | 📄 Document Processing 10 | 🤖 Quant Tools 8 | 📰 News & Sentiment 7 | 📎 Others 139
>
> Below are core category examples. **For complete list, see `skills/` directory**.

### 1. Data Sources (60)

#### Unified Data Abstraction Layer (1)

| Skill | Description |
|:---|:---|
| `cn-stock-data` | Unified data abstraction layer for A-share/HK/US stocks, shielding underlying API differences, providing unified code format, field names, smart routing and auto fallback |

#### Self-built Data Sources (5)

| Skill | Source | Core Capabilities |
|:---|:---|:---|
| `akshare-finance` | AkShare | Stock/futures/options/fund/forex/bond/index/crypto quotes and fundamentals |
| `efinance-data` | efinance | A-share quotes/capital flow (main/large/super large)/dragon-tiger/top 10 holders/earnings/fund/convertible bonds/futures |
| `adata-source` | adata | A-share quotes/northbound real-time data/hot rankings/43-field core financial metrics/concept sectors |
| `pysnowball-data` | Xueqiu | A/HK/US cross-market quotes + financial statements + industry comparison (some APIs require token) |
| `ashare-data` | Sina+Tencent | Ultra-lightweight K-line fallback solution, zero dependencies, supports daily/weekly/monthly/minute K-lines |

---

## 🎯 Use Cases

### Case 1: Multi-dimensional Stock Analysis
Query Moutai from multiple angles: fundamentals + technicals + capital flows

### Case 2: Sector Leader Comparison
Compare leading stocks across sectors with key metrics

### Case 3: Macro Dashboard
Economic cycle judgment and macro indicators monitoring

---

## 🔧 Troubleshooting

| Issue | Solution |
|:---|:---|
| OpenClaw not installed | Run `curl -fsSL https://openclaw.ai/install.sh \| bash` first |
| OpenClaw startup failed | Check port usage: `openclaw logs` to view logs |
| Python dependencies missing | `pip install akshare pandas requests` |
| AkShare data empty | Check AkShare version `pip install -U akshare` |
| Skills not found | Confirm path: `~/.openclaw/workspace/FinClaw/skills` |

### Check Installation Status

```bash
# Check if OpenClaw is installed
openclaw version

# Check if skills are correctly placed
openclaw config get skills.load.extraDirs

# Check Python dependencies
python -c "import akshare; print(akshare.__version__)"
```

---

## 📅 Roadmap

- ✅ **Completed**: 960 Skills (data sources/research/quant/insurance/banking/assistants/tools), unified data abstraction layer, environment variable-driven paths, Docker deployment
- 🚧 **In Progress**: Web visualization interface, FinSkillsHub


---

## 🤝 Contributing

Welcome to submit Issues and PRs!

```bash
git checkout -b feature/your-feature
npm test
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

---

## 📄 License

[Apache 2.0](LICENSE) © 2026 FinClaw Contributors

---
