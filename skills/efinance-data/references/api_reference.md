# efinance API 速查手册

## 安装

```bash
pip install efinance pandas
```

## 模块结构

```
efinance
├── stock   — A股/港股/美股
├── fund    — 公募基金
├── bond    — 可转债
└── futures — 期货
```

## 股票模块 (ef.stock)

| 函数 | 说明 | 参数 |
|------|------|------|
| `get_realtime_quotes()` | A股实时行情（全市场） | 无 |
| `get_quote_history(code)` | 历史K线 | code, klt(101日/102周/103月), beg, end |
| `get_quote_snapshot(code)` | 实时快照 | code |
| `get_base_info(code)` | 基本信息（PE/PB/ROE/行业） | code |
| `get_top10_stock_holder_info(code)` | 十大股东 | code |
| `get_history_bill(code)` | 历史资金流向 | code |
| `get_today_bill(code)` | 当日分时资金流 | code |
| `get_daily_billboard()` | 龙虎榜 | 无 |
| `get_all_company_performance()` | 全市场业绩报表 | 无 |
| `get_latest_holder_number(code)` | 股东人数 | code |
| `get_latest_ipo_info()` | 最新IPO | 无 |
| `get_belong_board(code)` | 所属板块 | code |
| `get_deal_detail(code)` | 逐笔成交 | code |
| `get_members(board_code)` | 板块成分股 | board_code |

### 实时行情返回字段

股票代码, 股票名称, 涨跌幅, 最新价, 最高, 最低, 今开, 涨跌额, 换手率, 量比, 动态市盈率, 成交量, 成交额, 昨日收盘, 总市值, 流通市值, 行情ID, 市场类型, 更新时间, 最新交易日

### 资金流向返回字段

股票名称, 股票代码, 日期, 主力净流入, 小单净流入, 中单净流入, 大单净流入, 超大单净流入, 主力净流入占比, 小单流入净占比, 中单流入净占比, 大单流入净占比, 超大单流入净占比, 收盘价, 涨跌幅

### 基本信息返回字段

股票代码, 股票名称, 净利润, 总市值, 流通市值, 所处行业, 市盈率(动), 市净率, ROE, 毛利率, 净利率, 板块编号

### 业绩报表返回字段

股票代码, 股票简称, 公告日期, 营业收入, 营业收入同比增长, 营业收入季度环比, 净利润, 净利润同比增长, 净利润季度环比, 每股收益, 每股净资产, 净资产收益率, 销售毛利率, 每股经营现金流量

## 基金模块 (ef.fund)

| 函数 | 说明 | 参数 |
|------|------|------|
| `get_quote_history(code)` | 基金净值历史 | code |
| `get_quote_history_multi(codes)` | 批量净值历史 | codes (list) |
| `get_invest_position(code)` | 重仓股持仓 | code |
| `get_industry_distribution(code)` | 行业分布 | code |
| `get_fund_manager(code)` | 基金经理 | code |
| `get_period_change(code)` | 阶段涨幅 | code |
| `get_base_info(code)` | 基金基本信息 | code |
| `get_fund_codes()` | 基金代码列表 | 无 |
| `get_realtime_increase_rate(codes)` | 实时涨幅 | codes (list, 必填) |
| `get_types_percentage(code)` | 资产配置比例 | code |
| `get_public_dates(code)` | 公告日期 | code |
| `get_pdf_reports(code)` | PDF报告 | code |

## 债券模块 (ef.bond)

| 函数 | 说明 | 参数 |
|------|------|------|
| `get_realtime_quotes()` | 可转债实时行情 | 无 |
| `get_quote_history(code)` | 可转债历史K线 | code |
| `get_all_base_info()` | 全部可转债信息 | 无 |
| `get_base_info(code)` | 单只可转债信息 | code |
| `get_history_bill(code)` | 可转债资金流 | code |
| `get_deal_detail(code)` | 逐笔成交 | code |
| `get_today_bill(code)` | 当日资金流 | code |

## 期货模块 (ef.futures)

| 函数 | 说明 | 参数 |
|------|------|------|
| `get_realtime_quotes()` | 期货实时行情 | 无 |
| `get_quote_history(code)` | 期货历史K线 | code |
| `get_futures_base_info()` | 期货品种信息 | 无 |
| `get_deal_detail(code)` | 逐笔成交 | code |

## 代码示例

### 投资组合监控

```python
import efinance as ef

# 批量获取自选股行情
df = ef.stock.get_realtime_quotes()
watchlist = ["000001", "600519", "000858"]
my_stocks = df[df["股票代码"].isin(watchlist)]
print(my_stocks[["股票代码", "股票名称", "最新价", "涨跌幅", "动态市盈率"]])
```

### 资金流向分析

```python
import efinance as ef

# 查看平安银行最近30天资金流
df = ef.stock.get_history_bill("000001")
df_recent = df.tail(30)
# 主力净流入为正 = 主力买入
bullish_days = df_recent[df_recent["主力净流入"] > 0]
print(f"最近30天主力净流入天数: {len(bullish_days)}")
```

### 基金持仓对比

```python
import efinance as ef

# 对比两只基金的重仓股
for code in ["005827", "110011"]:
    pos = ef.fund.get_invest_position(code)
    print(f"\n基金 {code} 重仓股:")
    print(pos.head(10))
```

## 已知问题

1. `get_realtime_increase_rate()` 需要传入基金代码列表参数，不能空调用
2. 可转债 `get_realtime_quotes()` 在非交易时段可能返回 JSON 解析错误
3. 基金净值历史返回数据按时间倒序排列（最新在前）
4. 期货代码格式为中文品种名+合约月份，如 "棕榈油2509"
