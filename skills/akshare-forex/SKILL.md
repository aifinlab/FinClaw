# AkShare 外汇数据 Skill

基于 AkShare 的外汇数据获取工具，覆盖全球主要货币对汇率。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **中国银行**: 外汇牌价

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `forex_quote.py` | 汇率行情 | `python forex_quote.py` |
| `forex_boc.py` | 中国银行牌价 | `python forex_boc.py` |

## 支持的货币对

| 货币对 | 说明 |
|:---|:---|
| USD/CNY | 美元兑人民币 |
| EUR/CNY | 欧元兑人民币 |
| JPY/CNY | 日元兑人民币 |
| GBP/CNY | 英镑兑人民币 |
| EUR/USD | 欧元兑美元 |
| USD/JPY | 美元兑日元 |

## 快速开始

```bash
# 获取汇率
python scripts/forex_quote.py

# 中国银行牌价
python scripts/forex_boc.py
```

## 许可证
MIT
