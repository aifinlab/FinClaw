<div align="center">
  <div style="font-size: 120px;">🦞</div>
</div>

# FinClaw 🦞 | 开源金融数据投研平台

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](package.json)
[![Skills](https://img.shields.io/badge/Skills-960个-blueviolet.svg)](#-skills-全景目录960个)
[![Free](https://img.shields.io/badge/免费-0元-brightgreen.svg)]()

> **开箱即用的金融数据投研神器** —— **960 个 Skills**，覆盖 A股投研/量化策略/数据源/保险/银行/投研助手/通用工具全品类，**无需 API Key，一键上手！**

[English](README_EN.md) | [中文](README.md)

---

## 🚀 快速开始

FinClaw 是基于 **OpenClaw** 开发的金融数据 Skills 集合，必须基于 OpenClaw 运行。

### 安装部署

**标准安装（推荐）**

```bash
# 1. 安装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. 进入 workspace 目录
cd ~/.openclaw/workspace

# 3. 克隆 FinClaw 项目
git clone https://github.com/aifinlab/FinClaw .

# 4. 安装 Python 依赖
pip install akshare pandas numpy requests

# 5. 启动 OpenClaw
openclaw start
```

**Docker 部署**

```bash
# 1. 启动 OpenClaw 容器
docker run -d --name openclaw -p 18789:18789 openclaw/openclaw:latest

# 2. 复制 FinClaw 到容器
docker exec openclaw mkdir /home/node/.openclaw/workspace/
docker cp ./FinClaw openclaw:/home/node/.openclaw/workspace/FinClaw

# 3. 重启容器
docker restart openclaw
```

### 使用方法

**方式一：通过 OpenClaw Agent 调用（推荐）**

启动后，直接在对话中与 OpenClaw 交互：
- "查询茅台股票行情"
- "帮我做贵州茅台的 DCF 估值"
- "分析北向资金近期动向"
- "用动量策略回测沪深300成分股"

**方式二：命令行直接运行 Skills**

```bash
# 查看所有 skills
ls -1 skills/

# 按类别查找
ls -1 skills/ | grep "^bank-"        # 银行业务
ls -1 skills/ | grep "^a-share-"     # A股相关
ls -1 skills/ | grep "^fund-"        # 基金相关
```

---

## 🚀 四大核心亮点

### 1️⃣ 960 个 Skills 全品类覆盖

| 类别 | 数量 | 覆盖内容 |
|:---|:---:|:---|
| 🏦 **银行业务** | 134 | 对公金融/零售金融/财富管理/风险管理/合规运营/交易银行全业务线 |
| 💼 **投研与财富管理** | 122 | 投研助手/财富管理/客户服务/资产配置/组合诊断/陪伴内容 |
| 🗄️ **数据源** | 60 | 统一抽象层 + AkShare + 东财/同花顺/巨潮/FRED/ECB/BOJ |
| 📑 **尽调与项目管理** | 57 | 尽调问题清单/项目准入/融资实体DD/持续监控/项目归档 |
| 🛡️ **保险业务** | 55 | 核保/理赔/产品对比/保障分析/营销/合规/风险识别 |
| 📊 **A股投研** | 54 | 估值/财报/行业/技术/资金/情绪/宏观/选股/组合/期权 |
| 🔢 **A股量化** | 50 | 因子/策略/风险/数据挖掘/板块量化/交易信号/财务量化 |
| 🔧 **数据处理与全局工具** | 47 | 全局检索/数据清洗/实体识别/字段映射/知识分块 |
| 🎯 **产品与营销** | 43 | 产品管理/营销机会/销售话术/路演支持/竞品追踪 |
| 📋 **合规与审计** | 37 | 合规审查/监管报送/审计追溯/审批流程/质量校验 |
| 📈 **基金业务** | 35 | 基金诊断/持仓陪伴/公告解读/渠道FAQ/产品定位 |
| ⚠️ **风险管理** | 25 | 风险预警/风险归因/风险日报/风险阈值监控/压力测试 |
| 🧰 **通用工具** | 24 | MCP/API/前端/文档处理/Skill创建/可视化设计 |
| 🏛️ **信托业务** | 20 | 家族信托/信托方案/受托报告/信托政策/慈善信托 |
| 📞 **运营服务** | 17 | 会议纪要/服务流程/运营报告/客户沟通/满意度洞察 |
| 🚨 **异常监测** | 16 | 异常交易/账户监控/行为关联/高频撤单/欺诈识别 |
| 📄 **文档处理** | 10 | PDF/Word/Excel/OCR/表格识别/版本对比 |
| 🤖 **量化工具** | 8 | 回测/因子/AI选股/组合优化/事件研究/可视化 |
| 📰 **新闻舆情** | 7 | 财经新闻/舆情分析/东财股吧/微博/雪球/情感监测 |
| 📎 **其他** | 139 | 各类专项业务场景/行业特定工具/定制化解决方案 |

**全部免费** · **无需注册** · **即装即用**

---

### 2️⃣ 统一数据抽象层（cn-stock-data）

```
用户请求 → cn-stock-data（统一入口）→ 智能路由 → efinance / akshare / adata / ashare / snowball
```

| 数据类型 | 路由优先级 |
|:---|:---|
| K线行情 | efinance → akshare → adata → ashare → snowball |
| 实时报价 | efinance → adata → snowball |
| 跨市场(港/美) | snowball 独占 |

**统一代码格式（SH600519）、统一字段名（英文 snake_case）、自动 Fallback，上层 Skill 无需关心数据源差异。**

---
### 3️⃣ 开箱即用 —— 仅需一行命令
**无需 API Key，无需配置，安装即用！**

---
### 4️⃣ 功能齐全 —— 投研全链路
| 环节 | 覆盖内容 |
|:---|:---|
| **盘前** | 晨会纪要、财经新闻分析、业绩前瞻、宏观数据解读 |
| **盘中** | 北向资金、主力资金、龙虎榜、市场情绪、涨跌停追踪 |
| **盘后** | 个股复盘、周度复盘、技术分析、研报摘要、事件驱动 |
| **深度研究** | DCF估值、可比公司、财务健康、护城河、产业链、投资论点 |
| **量化策略** | 因子分析、动量/均值回归/趋势跟踪/配对交易、组合优化、风险归因 |
| **风控** | VaR分析、回撤分析、止损策略、尾部风险、仓位管理 |


## 🧠 Skills 全景目录（960个）

> **说明**：FinClaw 现已包含 **960 个 Skills**，分布如下：
> - 🏦 银行业务 134个 | 💼 投研与财富管理 122个 | 🗄️ 数据源 60个 | 📑 尽调与项目 57个 | 🛡️ 保险业务 55个
> - 📊 A股投研 54个 | 🔢 A股量化 50个 | 🔧 数据处理 47个 | 🎯 产品营销 43个 | 📋 合规审计 37个
> - 📈 基金业务 35个 | ⚠️ 风险管理 25个 | 🧰 通用工具 24个 | 🏛️ 信托业务 20个 | 📞 运营服务 17个
> - 🚨 异常监测 16个 | 📄 文档处理 10个 | 🤖 量化工具 8个 | 📰 新闻舆情 7个 | 📎 其他 139个
>
> 以下展示核心类别示例，**完整列表请查看 `skills/` 目录**。

### 一、数据源层（60 个）

#### 统一数据抽象层（1 个）

| Skill | 说明 |
|:---|:---|
| `cn-stock-data` | A股/港股/美股统一数据抽象层，屏蔽底层 API 差异，提供统一代码格式、统一字段名、智能路由和自动 Fallback |

#### 自建数据源（5 个）

| Skill | 数据源 | 核心能力 |
|:---|:---|:---|
| `akshare-finance` | AkShare | 股票/期货/期权/基金/外汇/债券/指数/加密货币行情与基本面 |
| `efinance-data` | efinance | A股行情/资金流（主力/大单/超大单）/龙虎榜/十大股东/业绩/基金/可转债/期货 |
| `adata-source` | adata | A股行情/北向资金实时数据/热门排行/43字段核心财务指标/概念板块 |
| `pysnowball-data` | 雪球 | A/港/美跨市场行情 + 财务三表 + 行业对比（部分接口需 token） |
| `ashare-data` | 新浪+腾讯 | 超轻量 K线回退方案，零依赖，支持日/周/月/分钟级 K线 |

#### AkShare 细分数据接口（29 个）

| Skill | 数据领域 | Skill | 数据领域 |
|:---|:---|:---|:---|
| `akshare-stock` | A股行情/板块/资金 | `akshare-fund` | 基金净值/排行/搜索 |
| `akshare-bond` | 债券数据 | `akshare-futures` | 期货行情 |
| `akshare-options` | 期权数据 | `akshare-index` | 指数数据 |
| `akshare-macro` | 宏观经济 | `akshare-industry` | 行业数据 |
| `akshare-concept` | 概念板块 | `akshare-capital` | 资金流向 |
| `akshare-margin` | 融资融券 | `akshare-holders` | 股东数据 |
| `akshare-lhb-detail` | 龙虎榜详情 | `akshare-news` | 财经新闻 |
| `akshare-report` | 研报数据 | `akshare-pledge` | 股权质押 |
| `akshare-qfii` | QFII 持仓 | `akshare-esg` | ESG 评分 |
| `akshare-reits` | REITs 数据 | `akshare-crypto` | 加密货币 |
| `akshare-forex` | 外汇数据 | `akshare-executive` | 高管信息 |
| `akshare-manager` | 基金经理 | `akshare-star` | 科创板 |
| `akshare-block-trade` | 大宗交易 | `akshare-survey` | 调研数据 |
| `akshare-fof` | FOF 基金 | `akshare-alerts` | 预警数据 |
| `akshare-allocation` | 配置数据 | | |

#### 其他第三方数据源（11 个）

| Skill | 说明 |
|:---|:---|
| `eastmoney-skill` | 东方财富综合数据 |
| `eastmoney-fund-skill` | 东财基金数据 |
| `eastmoney-fund-daily` | 东财基金每日净值 |
| `eastmoney-bond-skill` | 东财债券数据 |
| `ths-skill` | 同花顺数据接口 |
| `ths-edb-skill` | 同花顺经济数据库 |
| `tencent-bond-skill` | 腾讯债券数据 |
| `cninfo-skill` | 巨潮资讯数据 |
| `fred-data` | 美联储经济数据（FRED） |
| `ecb-data` | 欧央行经济数据 |
| `boj-data` | 日本央行经济数据 |

---

### 二、A股投研 Skills（54 个）

#### 估值与财务分析（12 个）

| Skill | 功能 |
|:---|:---|
| `a-share-dcf` | DCF 估值模型/现金流折现 |
| `a-share-comps` | 可比公司分析/行业估值对标 |
| `a-share-valuation-band` | 估值分位/历史估值区间 |
| `a-share-earnings-analysis` | 个股财报分析/业绩点评 |
| `a-share-earnings-preview` | 业绩前瞻/情景分析 |
| `a-share-earnings-calendar` | 财报日历/业绩预告汇总 |
| `a-share-financial-health` | 财务健康度/F-Score/爆雷预警 |
| `a-share-cash-flow` | 现金流分析/FCF 质量评估 |
| `a-share-growth-quality` | 成长质量/PEG 分析 |
| `a-share-dividend` | 分红/股息分析 |
| `a-share-dividend-calendar` | 分红日历/除权除息追踪 |
| `a-share-peer-compare` | 同行财务对比/两股 PK |

#### 个股深度研究（8 个）

| Skill | 功能 |
|:---|:---|
| `a-share-initiation` | 个股深度研究/首次覆盖报告 |
| `a-share-thesis` | 投资论点建立与追踪 |
| `a-share-competitive-moat` | 企业护城河/竞争优势分析 |
| `a-share-management-quality` | 管理层质量/公司治理 |
| `a-share-capital-allocation` | 资本配置/回购/并购分析 |
| `a-share-shareholder-structure` | 股权结构/筹码集中度 |
| `a-share-turnaround` | 困境反转/业绩拐点 |
| `a-share-risk-alert` | 风险预警/ST/退市风险排查 |

#### 行业与板块（7 个）

| Skill | 功能 |
|:---|:---|
| `a-share-sector` | 行业研究/板块分析 |
| `a-share-sector-rotation` | 行业轮动/风格切换 |
| `a-share-industry-chain` | 产业链/上下游梳理 |
| `a-share-concept` | 概念板块/题材分析 |
| `a-share-thematic-invest` | 主题投资/赛道分析 |
| `a-share-etf` | ETF 分析/行业 ETF 对比 |
| `a-share-cross-market` | 跨市场联动/AH 溢价 |

#### 资金与情绪（8 个）

| Skill | 功能 |
|:---|:---|
| `a-share-northbound` | 北向资金（沪深港通）分析 |
| `a-share-money-flow` | 主力资金/大单追踪 |
| `a-share-dragon-tiger` | 龙虎榜分析/游资追踪 |
| `a-share-margin-trading` | 融资融券/两融分析 |
| `a-share-insider` | 股东/高管增减持 |
| `a-share-fund-holding` | 公募基金持仓/机构追踪 |
| `a-share-sentiment` | 市场情绪/恐贪指数 |
| `a-share-market-breadth` | 市场宽度/涨跌家数 |

#### 技术面与行情（7 个）

| Skill | 功能 |
|:---|:---|
| `a-share-technical` | 技术分析/K线/均线/MACD |
| `a-share-board-analysis` | 涨跌停板/连板追踪 |
| `a-share-index-analysis` | 大盘/指数分析 |
| `a-share-stock-review` | 个股复盘/交易复盘 |
| `a-share-seasonal-pattern` | 季节性规律/日历效应 |
| `a-share-convertible-bond` | 可转债分析/转债策略 |
| `a-share-futures-analysis` | 股指期货/基差分析 |

#### 宏观与研报（5 个）

| Skill | 功能 |
|:---|:---|
| `a-share-macro` | 宏观经济分析/数据解读 |
| `a-share-morning-note` | 晨会纪要/盘前要点 |
| `a-share-weekly-review` | 周度复盘/每周总结 |
| `a-share-research-digest` | 研报摘要/卖方观点 |
| `a-share-regulatory-watch` | 监管追踪/问询函/处罚 |

#### 事件驱动与选股（4 个）

| Skill | 功能 |
|:---|:---|
| `a-share-event` | 事件驱动分析/公告解读 |
| `a-share-stock-screen` | 量化选股/股票筛选器 |
| `a-share-ipo` | IPO/新股分析 |
| `a-share-correlation` | 相关性/联动分析 |

#### 组合与期权（3 个）

| Skill | 功能 |
|:---|:---|
| `a-share-portfolio` | 投资组合管理/持仓分析 |
| `a-share-quant-backtest` | 量化策略回测 |
| `a-share-option-strategy` | 期权策略分析 |

---

### 三、A股量化 Skills（50 个）

#### 因子与模型（8 个）

| Skill | 功能 |
|:---|:---|
| `a-share-factor-analysis` | 单因子研究/IC 检验 |
| `a-share-multifactor-model` | 多因子模型/Barra 风格因子 |
| `a-share-factor-library` | 量化因子库/因子速查 |
| `a-share-factor-timing` | 因子择时/风格轮动 |
| `a-share-pairs-trading` | 配对交易/统计套利 |
| `a-share-alpha-decay` | Alpha 衰减/因子拥挤度 |
| `a-share-mean-reversion` | 均值回归/超跌反弹 |
| `a-share-event-quant` | 事件驱动量化/事件研究法 |

#### 策略（10 个）

| Skill | 功能 |
|:---|:---|
| `a-share-momentum-strategy` | 动量策略/反转效应 |
| `a-share-smart-money` | 聪明钱指标/主力行为量化 |
| `a-share-trend-following` | 趋势跟踪/趋势强度 |
| `a-share-money-rotation` | 资金轮动/板块资金流 |
| `a-share-breakout-strategy` | 突破策略/形态突破 |
| `a-share-index-enhance` | 指数增强/超额收益 |
| `a-share-multi-strategy` | 多策略组合/策略配置 |
| `a-share-volume-price` | 量价关系量化分析 |
| `a-share-signal-backtest` | 交易信号回测/策略验证 |
| `a-share-market-timing` | 择时策略/大盘择时 |

#### 风险与仓位（10 个）

| Skill | 功能 |
|:---|:---|
| `a-share-risk-attribution` | 绩效归因/Brinson 归因 |
| `a-share-portfolio-optimize` | 量化组合优化 |
| `a-share-volatility` | 波动率分析/GARCH 建模 |
| `a-share-drawdown-analysis` | 回撤分析/最大回撤统计 |
| `a-share-regime-detection` | 市场状态/牛熊识别 |
| `a-share-position-sizing` | 仓位管理/凯利公式 |
| `a-share-var-analysis` | VaR 风险价值/条件 VaR |
| `a-share-tail-risk` | 尾部风险/黑天鹅分析 |
| `a-share-beta-hedging` | Beta 对冲/市场中性 |
| `a-share-stop-loss` | 止损策略/风控规则 |

#### 数据挖掘（8 个）

| Skill | 功能 |
|:---|:---|
| `a-share-anomaly-detection` | 量价异常检测/异动监控 |
| `a-share-stock-clustering` | 股票聚类/相似股票发现 |
| `a-share-lead-lag` | 领先滞后/板块传导 |
| `a-share-earnings-surprise` | 业绩超预期/低预期分析 |
| `a-share-distribution-analysis` | 收益率分布/统计特征 |
| `a-share-cointegration-test` | 协整检验/长期均衡 |
| `a-share-autocorrelation` | 自相关/序列相关性 |
| `a-share-structural-break` | 结构变点/趋势拐点 |

#### 板块量化（6 个）

| Skill | 功能 |
|:---|:---|
| `a-share-sector-momentum` | 板块动量/行业轮动动量 |
| `a-share-sector-spread` | 板块价差/行业估值差 |
| `a-share-style-analysis` | 风格分析/Sharpe 归因 |
| `a-share-sector-fund-flow` | 行业资金流向/板块主力 |
| `a-share-concentration-index` | 市场集中度/筹码集中度 |
| `a-share-relative-strength` | 相对强弱/RS 分析 |

#### 交易信号（4 个）

| Skill | 功能 |
|:---|:---|
| `a-share-turnover-analysis` | 换手率/筹码松动分析 |
| `a-share-order-imbalance` | 委托不平衡/盘口分析 |
| `a-share-gap-analysis` | 跳空缺口/缺口策略 |
| `a-share-intraday-pattern` | 日内模式/分时走势 |

#### 财务量化（4 个）

| Skill | 功能 |
|:---|:---|
| `a-share-quality-factor` | 质量因子/盈利质量 |
| `a-share-value-trap` | 价值陷阱/低估值陷阱 |
| `a-share-earnings-momentum` | 盈利动量/业绩趋势 |
| `a-share-financial-forensic` | 财务异常/造假预警 |

---

### 四、财经新闻 Skills（2 个）

| Skill | 功能 |
|:---|:---|
| `finance-news-source` | 聚合 12+ 中文财经网站（财联社/华尔街见闻/东财/雪球/财新等），提供结构化新闻抓取 |
| `finance-news-analysis` | 新闻情感分析（利好/利空/中性）、影响评估、个股关联识别，生成投资简报 |

---

### 五、保险业务 Skills（21 个）

#### 核保与风控（6 个）

| Skill | 功能 |
|:---|:---|
| `anti-fraud-screening` | 保险欺诈风险筛查 |
| `high-risk-case-warning` | 高风险案件识别预警 |
| `medical-history-risk-review` | 既往病史核保风险评估 |
| `medical-report-analysis` | 体检报告异常指标解读 |
| `underwriting-conclusion-explanation` | 核保结论解读（加费/除外/拒保） |
| `underwriting-questionnaire-review` | 核保问卷审查/告知义务 |

#### 理赔服务（3 个）

| Skill | 功能 |
|:---|:---|
| `claims-case-summary` | 理赔案件摘要/进度追踪 |
| `claims-communication` | 理赔沟通指导/异议处理 |
| `claims-material-check` | 理赔材料预审/缺失提醒 |

#### 产品与保障分析（5 个）

| Skill | 功能 |
|:---|:---|
| `insurance-product-comparison` | 产品责任/费率/性价比对比 |
| `coverage-gap-analysis` | 家庭保障缺口分析 |
| `coverage-liability-matching` | 保额与责任匹配评估 |
| `coverage-scope-judgment` | 保险责任范围判定 |
| `product-matching` | 个性化产品匹配推荐 |

#### 保单服务与营销（5 个）

| Skill | 功能 |
|:---|:---|
| `policy-liability-qa` | 保单责任条款解读 |
| `policy-service-process` | 保全业务指导（变更/贷款/退保） |
| `renewal-management` | 续保管理/流失预警 |
| `marketing-target-screening` | 营销客群筛选/精准营销 |
| `agent-business-development` | 代理人展业支持/成交促成 |

#### 合规与销售管理（2 个）

| Skill | 功能 |
|:---|:---|
| `sales-misconduct-identification` | 销售误导行为识别 |
| `insurance-skill` | 保险综合分析 |

---

### 六、银行业务 Skills（5 个）

| Skill | 功能 |
|:---|:---|
| `banking-workflow-orchestrator` | 银行业务流程编排器，跨 Skill 链路串联执行 |
| `business-analysis` | 经营分析摘要生成 |
| `channel-and-transaction` | 渠道与交易分析 |
| `customer-management` | 客户管理分析 |
| `risk-and-compliance` | 风控与合规分析 |

---

### 七、投研助手 Skills（15 个）

| Skill | 功能 |
|:---|:---|
| `company-research-assistant` | 公司基本面研究/商业模式拆解/竞争力评估 |
| `industry-research-assistant` | 行业研究/赛道分析/竞争格局/SWOT/波特五力 |
| `research-report-draft-assistant` | 研报初稿撰写/深度报告框架 |
| `earnings-quick-commentary-assistant` | 财报快评/季报解读/超预期判断 |
| `morning-meeting-minutes-assistant` | 晨会纪要整理/会议重点提炼 |
| `investment-advisory-qa-assistant` | 投顾 Q&A 口径/客户异议处理 |
| `client-engagement-content-assistant` | 客户陪伴内容/回撤安抚/定投陪伴 |
| `due-diligence-question-list-assistant` | 尽调问题清单/访谈提纲 |
| `concentrated-position-warning-assistant` | 集中持仓风险预警 |
| `suitability-review-assistant` | 客户适当性审核/产品准入 |
| `margin-financing-risk-assistant` | 融资融券风险预警/维保比例监控 |
| `announcement-interpretation-assistant` | 公告解读 |
| `fundraising-document-comparison-assistant` | 募集文件对比 |
| `ipo-material-precheck-assistant` | IPO 材料预审 |
| `marketing-opportunity-assistant` | 营销机会发现 |

---

### 八、量化工具 Skills（8 个）

| Skill | 功能 |
|:---|:---|
| `backtrader-skill` | Backtrader 量化回测框架 |
| `portfolio-optimizer` | 组合优化器 |
| `factor-analysis` | 因子分析工具 |
| `event-study` | 事件研究法工具 |
| `technical-skill` | 技术指标计算 |
| `fund-backtest` | 基金回测 |
| `visualization` | 数据可视化 |
| `data-cleaner` | 数据清洗工具 |

---

### 九、舆情分析 Skills（4 个）

| Skill | 功能 |
|:---|:---|
| `sentiment-eastmoney` | 东方财富股吧舆情 |
| `sentiment-weibo` | 微博财经舆情 |
| `sentiment-xueqiu` | 雪球社区舆情 |
| `global-macro` | 全球宏观分析 |

---

### 十、通用工具 Skills（17 个）

| Skill | 功能 |
|:---|:---|
| `skill-creator` | Skill 创建/修改/评测 |
| `claude-api` | Claude API / Anthropic SDK 开发 |
| `mcp-builder` | MCP Server 构建 |
| `frontend-design` | 前端界面设计 |
| `web-artifacts-builder` | 多组件 Web 应用构建 |
| `webapp-testing` | Web 应用 Playwright 测试 |
| `pdf` | PDF 读取/合并/拆分/OCR |
| `docx` | Word 文档创建/编辑 |
| `xlsx` | Excel 电子表格处理 |
| `pptx` | PPT 演示文稿制作 |
| `doc-coauthoring` | 文档协作撰写 |
| `canvas-design` | 视觉海报/艺术设计 |
| `algorithmic-art` | 算法艺术/生成艺术 |
| `brand-guidelines` | Anthropic 品牌风格应用 |
| `theme-factory` | 主题样式工厂（10 种预设） |
| `internal-comms` | 内部沟通文档模板 |
| `slack-gif-creator` | Slack 动画 GIF 创建 |

---

### 十一、其他 Skills（9 个）

| Skill | 功能 |
|:---|:---|
| `ai-stock-pick` | AI 选股 |
| `commodity-chain` | 大宗商品产业链 |
| `fastgpt-skill` | FastGPT 集成 |
| `atomic-ryc` | 原子化任务（RYC） |
| `atomic-zlj` | 原子化任务（ZLJ） |
| `fund_task_zlj` | 基金任务（ZLJ） |
| `external` | 外部接口 |
| `wzy` | 自定义工具 |
| `regulatory-reporting-quality-validation-workspace` | 监管报送质量校验 |

---




## 🎯 实战案例

### 案例1：多维度个股分析
```bash
# 茅台基本面+技术面+资金面综合分析
cd ~/.openclaw/workspace/FinClaw/skills/akshare-stock/scripts
python stock_quote_tx.py 600519       # 实时行情
python stock_tech.py 600519           # 技术指标
cd ../akshare-capital/scripts
python capital_flow.py 600519         # 资金流向
```

### 案例2：行业龙头股对比
```bash
cd ~/.openclaw/workspace/FinClaw/skills/akshare-stock/scripts
python stock_compare.py --codes 600519,000858,002304 \
  --fields pe,pb,roe,revenue_growth
```

### 案例3：宏观仪表盘
```bash
cd ~/.openclaw/workspace/FinClaw/skills/akshare-macro/scripts
python macro_summary.py               # 经济周期判断
```

---

## 🔧 故障排查

| 问题 | 解决方案 |
|:---|:---|
| OpenClaw 未安装 | 先执行 `curl -fsSL https://openclaw.ai/install.sh \| bash` |
| OpenClaw 启动失败 | 检查端口占用：`openclaw logs` 查看日志 |
| Python依赖缺失 | `pip install akshare pandas requests` |
| AkShare数据为空 | 检查AkShare版本 `pip install -U akshare` |
| Skills 找不到 | 确认路径：`~/.openclaw/workspace/FinClaw/skills` |

### 检查安装状态

```bash
# 检查 OpenClaw 是否安装
openclaw version

# 检查 skills 是否正确放置
openclaw config get skills.load.extraDirs

# 检查 Python 依赖
python -c "import akshare; print(akshare.__version__)"
```

---

## 📅 路线图

- ✅ **已完成**：960 个 Skills（数据源/投研/量化/保险/银行/助手/工具）、统一数据抽象层、环境变量驱动路径、Docker 部署
- 🚧 **进行中**：Web 可视化界面、FinSkillsHub


---

## 🤝 贡献指南

欢迎提交Issue和PR！

```bash
git checkout -b feature/your-feature
npm test
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

---

## 📄 许可证

[Apache 2.0](LICENSE) © 2026 FinClaw Contributors

---
