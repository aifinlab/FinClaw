---
name: "baostock-history"
description: "Historical stock data via BaoStock. Complete adjusted price data for A-shares, indices, and funds. Best for backtesting."
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["baostock", "pandas"]
---

# baostock-history

Historical stock data skill powered by [BaoStock](http://baostock.com).

## Setup

### 1. Install Dependencies

```bash
pip install baostock pandas
```

### 2. No API Key Required

BaoStock is completely free and requires no registration or API key.

## Features

- **Historical Price Data** - Complete daily K-line data from IPO to present
- **Adjusted Prices** - Forward and backward adjusted prices for accurate backtesting
- **Index Data** - All major A-share indices
- **Fund Data** - ETF and LOF historical data
- **Quarterly/Annual Financial Data** - Financial statements
- **No Rate Limits** - Free and unlimited access

## Commands

### Query Historical Data
```bash
python scripts/bs_history.py <code> [start_date] [end_date] [adjust]
```

### Query Index Data
```bash
python scripts/bs_index.py <code> [start_date] [end_date]
```

### Query Fund Data
```bash
python scripts/bs_fund.py <code> [start_date] [end_date]
```

### Query Stock List
```bash
python scripts/bs_stock_list.py
```

### Query Financial Data
```bash
python scripts/bs_finance.py <code> [year] [quarter]
```

## Stock Code Format

BaoStock uses `.` format:
- **Shanghai A-shares**: `sh.600000` (浦发银行)
- **Shenzhen A-shares**: `sz.000001` (平安银行)
- **Shanghai Index**: `sh.000001` (上证指数)
- **Shenzhen Index**: `sz.399001` (深证成指)
- **ChiNext**: `sz.300001` (特锐德)
- **STAR Market**: `sh.688001` (华兴源创)

## Examples

```bash
# Historical price data (adjusted)
python scripts/bs_history.py sh.600519 2020-01-01 2024-03-12 2

# Index data
python scripts/bs_index.py sh.000001 2024-01-01 2024-03-12

# Fund data
python scripts/bs_fund.py sh.510300 2024-01-01 2024-03-12

# Stock list
python scripts/bs_stock_list.py

# Financial data
python scripts/bs_finance.py sh.600519 2023 4
```

## Adjust Price Types

| Type | Value | Description |
|:---|:---:|:---|
| No adjustment | 1 | Original prices |
| Forward adjusted | 2 | Adjusted forward from IPO (recommended for backtesting) |
| Backward adjusted | 3 | Adjusted backward from today |

## File Structure

```
baostock-history/
├── SKILL.md
└── scripts/
    ├── bs_history.py      # Historical K-line data
    ├── bs_index.py        # Index data
    ├── bs_fund.py         # Fund data
    ├── bs_stock_list.py   # Stock list
    └── bs_finance.py      # Financial data
```

## Data Sources

- **BaoStock** - Free historical data from Shanghai/Shenzhen exchanges

## Features

| Feature | BaoStock Advantage |
|:---|:---|
| **Complete History** | Data from IPO to present |
| **Adjusted Prices** | Forward/backward adjustment for splits/dividends |
| **No Limits** | Unlimited queries, no rate limiting |
| **No Registration** | Completely free, no API key needed |
| **High Quality** | Official exchange data |

## Comparison

| Feature | BaoStock | Tushare | AkShare |
|:---|:---|:---|:---|
| Cost | Free | Free/Paid | Free |
| Registration | No | Required | No |
| Adjusted Data | ✅ Excellent | ✅ Good | ⚠️ Limited |
| Historical Depth | ⭐⭐⭐ Full | ⭐⭐⭐ Full | ⭐⭐ Partial |
| Rate Limits | None | Yes | Yes |
| Best For | Backtesting | Quant analysis | Real-time |

## Notes

- Best suited for historical backtesting and research
- Adjusted price data is essential for accurate backtesting
- Data quality is very high (official exchange data)
- No real-time data, typically delayed by 1 day
- Data is updated after market close

## Links

- [BaoStock Website](http://baostock.com)
- [BaoStock Documentation](http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3)
