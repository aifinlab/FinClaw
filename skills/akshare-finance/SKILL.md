---
name: akshare-finance
description: AKShare财经数据接口库封装，提供股票、期货、期权、基金、外汇、债券、指数、加密货币等金融产品的基本面数据、实时和历史行情数据、衍生数据。
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires": { "pip": ["akshare>=1.12", "pandas>=1.5"] },
        "install":
          [
            {
              "id": "pip-install",
              "kind": "pip",
              "packages": ["akshare>=1.12", "pandas>=1.5"],
              "label": "安装AKShare依赖"
            }
          ]
      }
  }
keywords:
  - 股票
  - 财经
  - 行情
  - 加密货币
  - 宏观经济
  - AKShare
---

# AKShare财经数据技能

## 快速开始

```bash
# 安装依赖
pip install akshare pandas

# 测试安装
python -c "import akshare; print(akshare.__version__)"
```

## 核心功能

### 1. 股票行情

```python
import akshare as ak

# A股实时行情
stock_zh_a_spot_em()  # 东方财富A股

# 股票K线数据
stock_zh_kline(symbol="000001", period="daily", adjust="qfq")

# 港股行情
stock_hk_spot_em()  # 港股实时

# 美股
stock_us_spot()  # 美股实时
```

### 2. 宏观经济

```python
# GDP数据
macro_china_gdp()  # 中国GDP

# CPI通胀
macro_china_cpi()  # 中国CPI

# PMI采购经理指数
macro_china_pmi()  # 中国PMI

# 货币供应量
macro_china_m2()  # M2广义货币
```

### 3. 加密货币

```python
# 币种列表
crypto_binance_symbols()  # 币安交易对

# 实时价格
crypto_binance_btc_usdt_spot()  # BTC/USDT

# K线数据
crypto_binance_btc_usdt_kline(period="daily")
```

### 4. 外汇贵金属

```python
# 外汇汇率
forex_usd_cny()  # 美元兑人民币

# 贵金属
metals_shibor()  # 上海银行间拆借利率

# 金银价格
metals_gold()  # 国际金价
```

### 5. 财务数据

```python
# 股票基本面
stock_fundamental(symbol="000001")  # 基本面数据

# 估值指标
stock_valuation(symbol="000001")  # PE、PB等

# 盈利能力
stock_profit_em(symbol="000001")
```

## 常用组合

### 投资组合监控

```python
import akshare as ak
import pandas as pd

# 监控自选股
tickers = ["000001", "000002", "600519"]
for ticker in tickers:
    df = ak.stock_zh_kline(symbol=ticker, period="daily", adjust="qfq", start_date="20240101")
    latest = df.iloc[-1]
    print(f"{ticker}: 收盘价={latest['close']}, 涨跌幅={latest['pct_chg']}%")
```

### 市场概览

```python
# A股大盘
index_zh_a_spot()  # 大盘指数

# 涨跌幅排行
stock_zh_a_spot_em()[['代码', '名称', '涨跌幅']].sort_values('涨跌幅', ascending=False)
```

## 注意事项

1. **数据来源**: 公开财经网站，仅用于学术研究
2. **商业风险**: 投资有风险，决策需谨慎
3. **更新频率**: 实时数据可能有延迟
4. **数据验证**: 建议多数据源交叉验证

## 输出格式

默认返回Pandas DataFrame，可直接处理：

```python
df = ak.stock_zh_a_spot_em()
print(df.head())  # 查看前5行
print(df.columns)  # 查看列名
df.to_csv("data.csv")  # 保存CSV
```

## 参考文档

- AKShare文档: https://akshare.akfamily.xyz/
- GitHub: https://github.com/akfamily/akshare

## 使用示例

### 示例 1: 基本使用

```python
# 调用 skill
result = run_skill({
    "param1": "value1",
    "param2": "value2"
})
```

### 示例 2: 命令行使用

```bash
python scripts/run_skill.py --input data.json
```
