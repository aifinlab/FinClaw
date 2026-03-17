---
name: pysnowball-data
description: "雪球（Snowball）金融数据接口，提供 A 股/港股/美股实时行情、财务报表（资产负债/利润/现金流）、估值指标、资金流向、行业对比、基金净值、可转债、指数数据。当用户需要雪球数据、跨市场行情（A/港/美）、财务报表详情、或雪球独有的业务分析数据时使用此 skill。pysnowball 的独特优势：(1)跨市场覆盖（A/港/美）(2)财务三表完整数据 (3)行业对比分析 (4)机构持仓变动。注意：部分高级接口需要雪球 token，基础行情（quotec）无需 token。"
---

# pysnowball 雪球金融数据源

## 定位

pysnowball 封装了雪球（xueqiu.com）的数据接口，1.7k GitHub Stars。与 akshare/efinance/adata 互补，pysnowball 的独特价值在于：

- **跨市场**：A 股、港股、美股统一接口
- **财务三表**：资产负债表、利润表、现金流量表完整数据
- **行业对比**：同行业公司横向比较
- **机构持仓**：机构持仓变动追踪
- **雪球生态**：组合、关注列表等社交数据

## 依赖

```bash
pip install pysnowball
```

## Token 说明

pysnowball 分两类接口：

**无需 token**（直接可用）：
- `quotec` — 实时行情快照（最常用）

**需要 token**（大部分接口）：
- 财务报表、K线、资金流、行业对比等

获取 token：登录 xueqiu.com → 浏览器开发者工具 → Cookie 中的 `xq_a_token` 值。

```python
import pysnowball as ball
ball.set_token('xq_a_token=你的token值;')
```

## 脚本一览

| 脚本 | 用途 | 核心命令 |
|------|------|---------|
| `quote_data.py` | 行情数据（无需token） | quotec / multi_quotec |
| `finance_data.py` | 财务+高级数据（需token） | income / balance / cashflow / indicator / kline / capital / industry |

## 行情数据 (quote_data.py) — 无需 Token

```bash
# 单只股票实时行情
python quote_data.py quotec --code SH600519

# 多只股票
python quote_data.py quotec --code SH600519,SZ000001,HK00700

# 代码格式：SH=沪市 SZ=深市 HK=港股 .O/.N=美股(纳斯达克/纽交所)
```

返回字段：current(最新价), percent(涨跌幅), chg(涨跌额), volume, amount, market_capital, float_market_capital, turnover_rate, amplitude, open, last_close, high, low, avg_price, current_year_percent(年初至今涨幅)

这是所有免费数据源中**唯一同时支持 A/港/美三市场**的实时行情接口。

## 财务数据 (finance_data.py) — 需要 Token

### 财务三表
```bash
# 利润表
python finance_data.py income --code SH600519

# 资产负债表
python finance_data.py balance --code SH600519

# 现金流量表
python finance_data.py cashflow --code SH600519
```

### 核心指标
```bash
python finance_data.py indicator --code SH600519
```

### K线
```bash
python finance_data.py kline --code SH600519 --period day
```

### 资金流向
```bash
python finance_data.py capital --code SH600519
```

### 行业对比
```bash
python finance_data.py industry --code SH600519
```

### 机构持仓
```bash
python finance_data.py holders --code SH600519
```

## 代码格式

| 市场 | 前缀 | 示例 |
|------|------|------|
| 沪市 A 股 | SH | SH600519 |
| 深市 A 股 | SZ | SZ000001 |
| 港股 | HK | HK00700 |
| 纳斯达克 | .O 后缀 | AAPL.O |
| 纽交所 | .N 后缀 | BABA.N |

## 与其他数据源的互补关系

| 数据需求 | 优先用 | 原因 |
|---------|-------|------|
| A/港/美 跨市场行情 | pysnowball-data | 唯一统一接口 |
| 财务三表（有token时） | pysnowball-data | 数据结构最规范 |
| 行业横向对比 | pysnowball-data | 内置行业对比接口 |
| 免费无门槛行情 | efinance-data / akshare | 不需要 token |
| 北向资金 | adata-source | 更全面 |
| 宏观经济 | akshare-finance | pysnowball 无宏观 |

## 注意事项

1. Token 有时效性，过期后需重新获取
2. 高频调用可能触发雪球反爬机制
3. 非交易时段返回最近交易日数据
4. 美股代码格式特殊（.O / .N 后缀）
