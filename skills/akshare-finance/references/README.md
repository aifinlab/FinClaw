# AKShare参考文档

## 安装

```bash
pip install akshare pandas
```

## 常用API速查

### 股票
| 函数 | 说明 | 示例 |
|-----|------|-----|
| stock_zh_a_spot_em() | A股实时行情 | df = stock_zh_a_spot_em() |
| stock_zh_kline() | K线数据 | stock_zh_kline(symbol="000001") |
| stock_hk_spot_em() | 港股实时 | stock_hk_spot_em() |

### 加密货币
| 函数 | 说明 | 示例 |
|-----|------|-----|
| crypto_binance_btc_usdt_spot() | BTC实时 | df = crypto_binance_btc_usdt_spot() |
| crypto_binance_btc_usdt_kline() | BTC K线 | crypto_binance_btc_usdt_kline(period="daily") |

### 宏观经济
| 函数 | 说明 | 示例 |
|-----|------|-----|
| macro_china_gdp() | GDP | macro_china_gdp() |
| macro_china_cpi() | CPI通胀 | macro_china_cpi() |
| macro_china_pmi() | PMI指数 | macro_china_pmi() |

### 外汇贵金属
| 函数 | 说明 | 示例 |
|-----|------|-----|
| forex_usd_cny() | 美元兑人民币 | forex_usd_cny() |
| metals_gold() | 黄金价格 | metals_gold() |

## 数据格式

所有函数返回Pandas DataFrame：

```python
df = ak.stock_zh_a_spot_em()
print(df.head())  # 前5行
print(df.columns) # 列名
print(df.dtypes)   # 数据类型
```

## 注意事项

1. 数据来源：公开财经网站
2. 更新延迟：实时数据可能有延迟
3. 使用限制：请参考官方文档
