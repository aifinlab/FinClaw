---
name: adata-source
description: "adata 免费A股量化数据源，专注A股市场，提供股票行情、资金流向、核心财务指标（43个字段）、北向资金、热门股票排行、分红数据、概念板块、指数成分股、基金及可转债数据。当用户需要A股行情、资金流、北向资金、热门排行、财务指标、分红信息时可使用此 skill。与 akshare-finance 和 efinance-data 互补——adata 的独特优势在于：(1)北向资金实时数据 (2)热门股票排行 (3)核心财务指标一次返回43个字段（EPS/ROE/毛利率/资产负债率/周转率等）(4)概念板块成分股。"
---

# adata A股量化数据源

## 定位

adata 是专注 A 股的免费量化数据库（4.1k GitHub Stars），数据来源为东方财富、同花顺等公开平台。与 akshare/efinance 互补，adata 在以下方面有独特优势：

- **北向资金**：沪股通/深股通净买入、累计流入
- **热门排行**：东方财富热门股 TOP 100
- **财务指标**：单次调用返回 43 个字段（EPS、ROE、毛利率、资产负债率、周转天数等）
- **概念板块**：东方财富/同花顺概念板块及成分股

## 依赖

```bash
pip install adata pandas
```

## 脚本一览

| 脚本 | 用途 | 核心命令 |
|------|------|---------|
| `stock_data.py` | 股票行情/资金流/财务/分红 | list / market / capital / finance / dividend / board |
| `sentiment_data.py` | 北向资金/热门排行 | north / hot |
| `fund_bond_data.py` | 基金和可转债 | fund_info / bond_info |

## 股票数据 (stock_data.py)

### 股票列表
```bash
python stock_data.py list
```
返回：stock_code, short_name, exchange, list_date（全部A股）

### 个股行情
```bash
# 日线行情
python stock_data.py market --code 000001 --start 2026-01-01

# 分钟级行情
python stock_data.py market_min --code 000001
```
返回：open, close, high, low, volume, amount, change_pct, turnover_ratio

### 资金流向
```bash
# 历史资金流（主力/小单/中单/大单/超大单）
python stock_data.py capital --code 000001

# 当日分钟级资金流
python stock_data.py capital_min --code 000001
```

### 核心财务指标（43个字段）
```bash
python stock_data.py finance --code 000001
```
这是 adata 最有价值的接口，单次返回：
- 每股指标：basic_eps, diluted_eps, non_gaap_eps, net_asset_ps, oper_cf_ps
- 营收利润：total_rev, gross_profit, net_profit_attr_sh, non_gaap_net_profit
- 增长率：total_rev_yoy_gr, net_profit_yoy_gr（同比），qoq_gr（环比）
- 盈利能力：roe_wtd, roa_wtd, gross_margin, net_margin
- 偿债能力：curr_ratio, quick_ratio, asset_liab_ratio
- 运营效率：total_asset_turn_days, inv_turn_days, acct_recv_turn_days

### 分红
```bash
python stock_data.py dividend --code 000001
```

### 所属板块/概念
```bash
# 概念板块成分股（东财）
python stock_data.py concept_members --concept BK0475

# 指数成分股
python stock_data.py index_members --index 000300
```

## 情绪数据 (sentiment_data.py)

### 北向资金
```bash
# 历史北向资金流入（沪股通/深股通/合计）
python sentiment_data.py north

# 当日实时北向资金
python sentiment_data.py north_current

# 分钟级北向资金
python sentiment_data.py north_min
```
返回：net_hgt（沪股通净买入）, net_sgt（深股通净买入）, net_tgt（合计）

### 热门股票
```bash
# 东方财富热门 TOP 100
python sentiment_data.py hot
```
返回：rank, stock_code, short_name, price, change_pct

## 基金和可转债 (fund_bond_data.py)

```bash
# 基金信息
python fund_bond_data.py fund_info --code 005827

# 可转债信息
python fund_bond_data.py bond_info --code 123456
```

## 与其他数据源的互补关系

| 数据需求 | 优先用 | 原因 |
|---------|-------|------|
| 北向资金（实时/分钟级） | adata-source | akshare 有日级，adata 有分钟级 |
| 热门股票排行 | adata-source | 其他源无此接口 |
| 核心财务43字段 | adata-source | 单次调用最全，含周转/偿债指标 |
| 概念板块成分股 | adata-source | 东财/同花顺双源 |
| 财务三表完整数据 | akshare-finance | adata 只有核心指标 |
| 资金流分层 | efinance-data | efinance 字段更细致 |
| 宏观经济 | akshare-finance | adata 无宏观数据 |
| 估值历史序列 | akshare-finance | adata 动态指标接口不稳定 |

## 注意事项

1. 数据来源为东方财富等公开网站，仅限学术研究
2. 部分接口首次调用需缓存，可能较慢
3. 概念板块缓存文件首次需生成，如报 FileNotFoundError 可忽略
4. 非交易时段实时数据可能为空或返回上一交易日数据
