# AkShare 指数数据 Skill

基于 AkShare 的指数数据获取工具，覆盖中证、上证系列指数。

## 数据源
- **AkShare**: https://www.akshare.xyz

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `index_quote.py` | 指数行情 | `python index_quote.py 000001` |
| `index_components.py` | 指数成分股 | `python index_components.py 000300` |
| `index_valuation.py` | 指数估值 | `python index_valuation.py` |

## 支持的指数

| 指数 | 代码 | 说明 |
|:---|:---|:---|
| 上证指数 | 000001 | 上海证券交易所综合指数 |
| 深证成指 | 399001 | 深圳证券交易所成份指数 |
| 创业板指 | 399006 | 创业板指数 |
| 沪深300 | 000300 | 沪深300指数 |
| 中证500 | 000905 | 中证500指数 |
| 上证50 | 000016 | 上证50指数 |
| 科创50 | 000688 | 科创50指数 |

## 快速开始

```bash
# 获取指数行情
python scripts/index_quote.py 000300

# 获取成分股
python scripts/index_components.py 000300

# 获取估值
python scripts/index_valuation.py
```

## 许可证
MIT
