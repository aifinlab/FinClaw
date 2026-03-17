# AkShare 加密货币数据 Skill

基于 AkShare 的加密货币数据获取工具，覆盖BTC、ETH等主流币种。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **币安**: 实时行情、K线数据
- **火币**: 实时行情、K线数据

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `crypto_quote.py` | 加密货币行情 | `python crypto_quote.py BTC` |
| `crypto_hist.py` | 历史K线数据 | `python crypto_hist.py BTC` |
| `crypto_market.py` | 市场概览 | `python crypto_market.py` |

## 支持的币种

| 币种 | 代码 |
|:---|:---|
| 比特币 | BTC |
| 以太坊 | ETH |
| 泰达币 | USDT |
| 币安币 | BNB |
| 瑞波币 | XRP |
| 索拉纳 | SOL |

## 快速开始

```bash
# 获取BTC行情
python scripts/crypto_quote.py BTC

# 获取ETH历史数据
python scripts/crypto_hist.py ETH

# 获取市场概览
python scripts/crypto_market.py
```

## 许可证
MIT
