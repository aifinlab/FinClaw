# 字段映射参考文档

## K线字段映射

| 统一字段 | efinance | akshare | adata | ashare | snowball |
|---------|---------|---------|-------|--------|----------|
| `date` | 日期 | 日期 | trade_date | (index) | timestamp |
| `open` | 开盘 | 开盘 | open | open | open |
| `close` | 收盘 | 收盘 | close | close | close |
| `high` | 最高 | 最高 | high | high | high |
| `low` | 最低 | 最低 | low | low | low |
| `volume` | 成交量 | 成交量 | volume | volume | volume |
| `amount` | 成交额 | 成交额 | amount | — | amount |
| `pct_change` | 涨跌幅 | 涨跌幅 | change_pct | — | percent |
| `change` | 涨跌额 | 涨跌额 | — | — | — |
| `turnover_rate` | 换手率 | 换手率 | turnover_ratio | — | turnover_rate |
| `amplitude` | 振幅 | 振幅 | — | — | — |

## 实时行情字段映射

| 统一字段 | efinance | adata | snowball |
|---------|---------|-------|----------|
| `code` | 股票代码 | stock_code | symbol |
| `name` | 股票名称 | short_name | name |
| `price` | 最新价 | trade_price | current |
| `pct_change` | 涨跌幅 | change_pct | percent |
| `change` | 涨跌额 | — | chg |
| `open` | 今开 | open | open |
| `high` | 最高 | high | high |
| `low` | 最低 | low | low |
| `pre_close` | 昨日收盘 | pre_close | last_close |
| `volume` | 成交量 | volume | volume |
| `amount` | 成交额 | amount | amount |
| `turnover_rate` | 换手率 | turnover_ratio | turnover_rate |
| `pe_ttm` | 动态市盈率 | — | — |
| `market_cap` | 总市值 | — | market_capital |
| `float_market_cap` | 流通市值 | — | float_market_capital |

## 资金流向字段映射

| 统一字段 | efinance | adata | snowball |
|---------|---------|-------|----------|
| `date` | 日期 | trade_date | timestamp |
| `main_net_inflow` | 主力净流入 | main_net_inflow | net_amount |
| `small_net_inflow` | 小单净流入 | — | — |
| `mid_net_inflow` | 中单净流入 | — | — |
| `large_net_inflow` | 大单净流入 | — | — |
| `xlarge_net_inflow` | 超大单净流入 | — | — |

## 代码格式转换

| 统一格式 | akshare/efinance/adata | ashare | snowball |
|---------|----------------------|--------|----------|
| `SH600519` | `600519` | `sh600519` | `SH600519` |
| `SZ000001` | `000001` | `sz000001` | `SZ000001` |
| `HK00700` | ❌ 不支持 | ❌ 不支持 | `HK00700` |
| `AAPL.O` | ❌ 不支持 | ❌ 不支持 | `AAPL.O` |

## 日期格式

所有返回结果统一为 `YYYY-MM-DD` 格式。调用各源时按需转换：
- efinance/akshare: `YYYYMMDD`（调用时去掉横线）
- adata: `YYYY-MM-DD`（原样透传）
- ashare: `YYYY-MM-DD`（原样透传）
- snowball: 毫秒时间戳（返回后转换）
