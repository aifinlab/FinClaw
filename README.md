<div align="center">
  <div style="font-size: 120px;">🦞</div>
</div>

# FinClaw 🦞 | 首个开源金融龙虾，1000+ 金融专属Skills全量免费

[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)](package.json)
[![Skills](https://img.shields.io/badge/Skills-1000%2B-blueviolet.svg)](#-skills-分类概览)
[![Free](https://img.shields.io/badge/免费-0元-brightgreen.svg)]()

> **开箱即用的金融数据投研神器** —— **1000+ 金融 Skills，6 只金融龙虾**，覆盖 **银行、券商、保险、基金、期货、信托**全品类，赋能全赛道金融人！**无需 API Key，一键上手！**

FinClaw 是首个面向金融行业的开源系统执行框架，由上海财经大学统计与数据科学学院、上海金融智能工程技术研究中心主任张立文教授领衔的人工智能金融实验室（AIFinLab）联合研发。

[English](README_EN.md) | [中文](README.md)

---

## 💡 六只金融龙虾

| 龙虾 | 定位 | 核心能力 |
|:---|:---|:---|
| 🦞 **银行龙虾** | 对公授信+自营投资专属智囊 | 授信审批、行业研究、资产配置、信用风险监测 |
| 🦞 **基金龙虾** | 净值归因+业绩诊断精准手术刀 | 投研回测、绩效归因、持仓合规、FOF组合构建 |
| 🦞 **证券龙虾** | 投研研判+业务拓展精准雷达 | 投行尽调、行业投研、机构路演、两融业务 |
| 🦞 **保险龙虾** | 负债匹配+资产配置定制专家 | 产品对比、保障分析、核保理赔、合规风控 |
| 🦞 **信托龙虾** | 非标业务+财富传承专属架构师 | 家族信托、非标估值、ABS测算、政信风控 |
| 🦞 **期货龙虾** | 行情复盘+交易研判全天候操盘手 | 主力合约复盘、跨期价差、产业驱动分析 |

---

## 🎯 精选60个金融Skills

覆盖六大金融板块，全部使用真实数据源。

### 银行套件 (10个)
| Skill | 功能描述 | 数据源 |
|:---|:---|:---|
| `bank-industry-analyzer` | 银行业整体分析（总资产、净利润、ROE） | 央行/金融监管总局 |
| `bank-financial-analyzer` | 单家银行财务分析 | 年报+腾讯行情 |
| `bank-valuation-analyzer` | 银行估值分析（PB/PE/股息率） | 实时行情+财务 |
| `bank-nim-analyzer` | 净息差(NIM)分析对比 | 银行年报 |
| `bank-risk-analyzer` | 风险指标分析（不良率/拨备覆盖率） | 银行年报 |
| `bank-liquidity-analyzer` | 流动性指标分析（LCR/NSFR） | 银行年报 |
| `bank-deposit-rates` | 存款利率查询对比 | 银行官网+LPR |
| `bank-interbank-market` | 银行间市场分析（Shibor/回购） | 交易中心 |
| `bank-credit-analyzer` | 信贷收支分析 | 央行统计 |
| `bank-wealth-products` | 理财产品分析 | 中国理财网 |

### 证券套件 (10个)
| Skill | 功能描述 | 数据源 |
|:---|:---|:---|
| `securities-industry-analyzer` | 证券业整体分析 | 证券业协会 |
| `securities-financial-analyzer` | 券商财务分析（ROE/杠杆率） | 年报数据 |
| `securities-valuation-analyzer` | 券商估值分析 | 实时行情+财务 |
| `securities-brokerage-analyzer` | 经纪业务分析（成交/市占率） | 交易所 |
| `securities-ib-analyzer` | 投行业务分析（IPO/承销） | 证券业协会 |
| `securities-margin-analyzer` | 两融业务分析 | 沪深交易所 |
| `securities-proprietary-analyzer` | 自营业务分析 | 券商年报 |
| `securities-am-analyzer` | 资管业务分析 | 中基协 |
| `securities-rating-analyzer` | 券商评级分析 | 证监会分类评价 |
| `securities-policy-analyzer` | 行业政策分析 | 监管公告 |

### 期货套件 (10个)
| Skill | 功能描述 | 数据源 |
|:---|:---|:---|
| `futures-market-overview` | 期货市场概览 | 五大交易所 |
| `commodity-futures-analyzer` | 商品期货分析（季节性/基差） | 交易所数据 |
| `financial-futures-analyzer` | 金融期货分析（股指期货基差） | 中金所 |
| `futures-volume-analyzer` | 成交持仓分析 | 交易所 |
| `futures-position-tracker` | 持仓追踪（龙虎榜） | 交易所 |
| `futures-arbitrage-analyzer` | 套利分析（跨品种/跨期） | 历史价差统计 |
| `futures-risk-analyzer` | 风险分析（VaR/波动率） | 历史数据 |
| `futures-margin-calculator` | 保证金计算器 | 交易所标准 |
| `futures-macro-correlation` | 宏观相关性分析 | 历史统计 |
| `futures-delivery-analyzer` | 交割分析 | 合约信息 |

### 保险套件 (10个)
| Skill | 功能描述 | 数据源 |
|:---|:---|:---|
| `insurance-market-overview` | 保险市场概览 | 金融监管总局 |
| `insurance-company-analyzer` | 保险公司分析 | 公司年报 |
| `insurance-life-analyzer` | 寿险业务分析（NBV/代理人） | 公司年报 |
| `insurance-pc-analyzer` | 财险业务分析（综合成本率） | 公司年报 |
| `insurance-investment-analyzer` | 投资资产配置分析 | 公司年报 |
| `insurance-valuation-analyzer` | 保险估值（PEV/内含价值） | 实时行情+精算 |
| `insurance-solvency-analyzer` | 偿付能力分析 | 偿付能力报告 |
| `insurance-policy-tracker` | 保单追踪分析 | 公司公告 |
| `insurance-sector-comparison` | 行业对比分析 | 行业统计 |
| `insurance-hot-events` | 热点事件分析 | 新闻舆情 |

### 基金套件 (10个)
| Skill | 功能描述 | 数据源 |
|:---|:---|:---|
| `fund-market-research` | 基金市场研究 | 中基协/三方 |
| `fund-screener` | 基金筛选器 | 多源数据 |
| `fund-risk-analyzer` | 基金风险分析（VaR/最大回撤） | 历史净值 |
| `fund-portfolio-allocation` | 资产配置（SAA/TAA/Markowitz） | 多源数据 |
| `fund-sip-planner` | 定投计划/智能定投 | 历史数据 |
| `fund-rebalance-advisor` | 再平衡顾问 | 持仓数据 |
| `fund-attribution-analysis` | 归因分析（Brinson/因子） | 持仓+收益 |
| `fund-holding-analyzer` | 持仓穿透分析 | 持仓数据 |
| `fund-tax-optimizer` | 税务优化（赎回/税损收割） | 交易记录 |
| `fund-monitor` | 基金监控预警 | 实时数据 |

### 信托套件 (10个)
| Skill | 功能描述 | 数据源 |
|:---|:---|:---|
| `trust-market-research` | 信托市场研究 | 用益信托/协会 |
| `trust-product-analyzer` | 信托产品分析 | 产品公告 |
| `trust-risk-manager` | 信托风险管理 | 多维度评估 |
| `trust-compliance-checker` | 合规审查 | 监管规则 |
| `trust-income-calculator` | 收益计算（IRR/XIRR） | 现金流 |
| `family-trust-designer` | 家族信托设计 | 规则引擎 |
| `charity-trust-manager` | 慈善信托管理 | 公益数据 |
| `trust-valuation-engine` | 估值引擎 | 多方法估值 |
| `trust-post-investment-monitor` | 投后监控 | 项目数据 |
| `trust-asset-allocation` | 资产配置优化 | 优化算法 |

---

## 🌟 核心亮点

### 1000+ Skills 全品类覆盖

| 类别 | 数量 | 覆盖内容 |
|:---|:---:|:---|
| 🏦 **银行业务** | 155 | 对公/零售/财富管理/风险管理/合规运营 |
| 💼 **投研助手** | 357 | 公司研究/行业研究/公告分析/尽职调查 |
| 📊 **A股投研** | 174 | 估值/财报/技术/资金/情绪/宏观/选股 |
| 🛡️ **保险业务** | 87 | 核保/理赔/产品/保障/营销/合规 |
| 📈 **基金业务** | 42 | 筛选/配置/定投/归因/监控 |
| 📉 **证券业务** | 20 | 经纪/投行/资管/融资融券 |
| 🏛️ **信托业务** | 20 | 产品分析/家族信托/投后监控 |
| 🗄️ **数据源** | 60 | AkShare/同花顺/东财/巨潮/FRED等 |
| ⚠️ **风控合规** | 33 | 合规检查/风险预警/监管报送 |
| 🧰 **通用工具** | 54 | 文档处理/前端设计/技能创建 |
| 📰 **舆情新闻** | 8 | 财经新闻/情感分析/舆情监控 |
| 🤖 **量化工具** | 8 | 回测/因子/组合优化/可视化 |
| 📎 **其他** | 7 | AI选股/商品数据/原子化任务 |

**全部免费 · 无需注册 · 即装即用**

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│  ① 用户交互层  │  飞书 / Discord / 微信 / CLI                    │
├─────────────────────────────────────────────────────────────────┤
│  ② OpenClaw   │  消息路由 / Session管理 / Skill注册 / 安全权限   │
├─────────────────────────────────────────────────────────────────┤
│  ③ FinClaw    │  SOUL人格 / 意图识别 / Skill调度 / 记忆管理      │
├─────────────────────────────────────────────────────────────────┤
│  ④ 数据层     │  统一接口 / 多源适配(AkShare/同花顺/腾讯等) / 故障转移│
├─────────────────────────────────────────────────────────────────┤
│  ⑤ 基础设施   │  LLM服务 / 文件存储 / 日志监控                   │
└─────────────────────────────────────────────────────────────────┘
```

**数据流**：用户输入 → 意图识别 → Skill调度 → 多源数据获取 → 格式化输出

---

## 🚀 快速开始

```bash
# 1. 安装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. 克隆 FinClaw
cd ~/.openclaw/workspace
git clone https://github.com/aifinlab/FinClaw .

# 3. 安装依赖
pip install akshare pandas numpy requests

# 4. 启动
openclaw start
```

**使用示例**：
- "查询茅台股票行情"
- "帮我做贵州茅台的 DCF 估值"
- "分析北向资金近期动向"

---

## 📁 项目结构

```
FinClaw/
├── skills/              # 1000+ 完整Skills目录
├── skillschoice/        # 精选60个金融Skills（6大套件）
│   ├── bank-suite/      # 银行套件 (10个)
│   ├── securities-suite/# 证券套件 (10个)
│   ├── futures-suite/   # 期货套件 (10个)
│   ├── insurance-suite/ # 保险套件 (10个)
│   ├── fund-suite/      # 基金套件 (10个)
│   └── trust-suite/     # 信托套件 (10个)
├── README.md            # 本文档
└── LICENSE              # Apache 2.0
```

---

## 🔧 故障排查

| 问题 | 解决方案 |
|:---|:---|
| OpenClaw 未安装 | `curl -fsSL https://openclaw.ai/install.sh \| bash` |
| Python依赖缺失 | `pip install akshare pandas requests` |
| Skills 找不到 | 确认路径：`~/.openclaw/workspace/FinClaw/skills` |

---

## 📅 路线图

- ✅ **已完成**：1000+ Skills、统一数据抽象层、Docker部署、精选60Skills
- 🚧 **进行中**：Web可视化界面、FinSkillsHub

---

## 🤝 贡献指南

欢迎提交Issue和PR！

```bash
git checkout -b feature/your-feature
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

---

## 📫 联系我们

诚邀业界同仁共同探索 AI 与金融深度融合的创新范式，共建智慧金融新生态。

📧 [zhang.liwen@shufe.edu.cn](mailto:zhang.liwen@shufe.edu.cn)

---

## 📄 许可证

[Apache 2.0](LICENSE) © 2026 FinClaw Contributors
