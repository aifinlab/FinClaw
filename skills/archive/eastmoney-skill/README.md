# eastmoney-skill

东方财富数据接口 Skill，提供免费的 A 股财务数据查询。

## 功能

- 获取股票基本信息
- 获取财务报表数据（资产负债表、利润表、现金流量表）
- 获取主要财务指标
- 获取最新公告

## 数据来源

使用东方财富公开的 API 接口（无需认证，免费使用）。

## 使用方法

```javascript
// 获取股票基本信息
const info = await eastmoney.getStockInfo('600519');

// 获取最新财务指标
const finance = await eastmoney.getMainFinance('600519');

// 获取最新公告
const announcements = await eastmoney.getAnnouncements('600519', { pageSize: 10 });
```

## API 说明

### getStockInfo(stockCode)
获取股票基本信息

**参数:**
- `stockCode` (string): 股票代码，如 '600519'

**返回:**
- 股票名称、所属行业、总市值、市盈率等

### getMainFinance(stockCode)
获取主要财务指标

**参数:**
- `stockCode` (string): 股票代码

**返回:**
- 营业收入、净利润、毛利率、ROE、资产负债率等

### getAnnouncements(stockCode, options)
获取公司公告

**参数:**
- `stockCode` (string): 股票代码
- `options.pageSize` (number): 返回条数，默认 10

**返回:**
- 公告标题、类型、发布时间、PDF 链接
