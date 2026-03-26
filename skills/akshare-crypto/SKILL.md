---
name: "akshare-crypto"
description: "加密货币Skill - 提供BTC、ETH等主流币种行情、K线数据、市场概览 via AkShare/币安/火币"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-crypto

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-crypto |
| **版本** | 1.1.0 |
| **分类** | 加密货币 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

加密货币Skill，提供比特币(BTC)、以太坊(ETH)等主流加密货币的实时行情、历史K线数据、市场概览。支持多交易所数据。

## 触发意图

### 主要触发词
- "比特币"、"BTC"、"以太坊"、"ETH"
- "加密货币"、"数字货币"、"虚拟币"
- "币安"、"火币"
- "区块链"、"挖矿"
- "USDT"、"稳定币"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 比特币价格多少？ | crypto_quote | crypto_quote.py BTC |
| 以太坊行情 | crypto_quote | crypto_quote.py ETH |
| BTC历史走势 | crypto_hist | crypto_hist.py BTC |
| 加密货币市场 | crypto_market | crypto_market.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 实时行情 | AkShare-币安 | AkShare-火币 | 无需 |
| 历史K线 | AkShare-币安 | AkShare-火币 | 无需 |
| 市场概览 | CoinMarketCap | - | 无需 |

## 支持的币种

| 币种 | 代码 | 类型 | 市值排名 |
|:---|:---|:---|:---:|
| 比特币 | BTC | 原生币 | 1 |
| 以太坊 | ETH | 智能合约平台 | 2 |
| 泰达币 | USDT | 稳定币 | 3 |
| 币安币 | BNB | 交易所代币 | 4 |
| 瑞波币 | XRP | 支付协议 | 5 |
| 索拉纳 | SOL | 智能合约平台 | 6 |
| 卡尔达诺 | ADA | 智能合约平台 | 7 |
| 狗狗币 | DOGE | Meme币 | 8 |
| 波卡 | DOT | 跨链协议 | 9 |
|  Polygon | MATIC | Layer2 | 10 |

## 功能列表

### 1. 加密货币行情
- **功能描述**: 获取主流加密货币实时行情
- **输入参数**: 币种代码（BTC/ETH等）
- **输出格式**: Markdown表格
- **数据源**: AkShare-币安/火币
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/crypto_quote.py BTC
  python scripts/crypto_quote.py ETH
  ```

### 2. 历史K线数据
- **功能描述**: 获取加密货币历史价格数据
- **输入参数**: 币种代码、时间周期、数据条数
- **输出格式**: CSV/Markdown表格
- **数据源**: AkShare-币安/火币
- **数据时效**: 历史数据
- **使用示例**:
  ```bash
  python scripts/crypto_hist.py BTC --period 1d --limit 365
  ```

### 3. 市场概览
- **功能描述**: 获取加密货币市场整体情况
- **输入参数**: 无
- **输出格式**: Markdown报告
- **数据源**: CoinMarketCap
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/crypto_market.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| crypto_quote.py | 加密货币行情 | ✅ |
| crypto_hist.py | 历史K线数据 | ✅ |
| crypto_market.py | 市场概览 | ✅ |

## 加密货币基础

### 主要类型
| 类型 | 代表 | 特点 |
|:---|:---|:---|
| **原生币** | BTC | 价值存储、数字黄金 |
| **智能合约平台** | ETH, SOL, ADA | 支持DApp和DeFi |
| **稳定币** | USDT, USDC | 锚定美元，波动小 |
| **交易所代币** | BNB | 交易平台权益 |
| **Meme币** | DOGE, SHIB | 社区驱动，波动大 |

### 24小时交易
加密货币市场**全天候24/7交易**，无涨跌幅限制。

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare-币安/火币
⏱️ **数据时间**: 2026-03-19
📌 **交易对**: BTC/USDT
🔗 **原始来源**: Binance/火币交易所
🔧 **分析工具**: FinClaw v1.0
⚠️ **风险提示**: 加密货币波动极大，投资需谨慎
```

## 依赖要求

```
akshare>=1.10.0
pandas>=1.3.0
pyyaml>=5.4.0
```

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
