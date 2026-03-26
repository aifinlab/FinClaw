---
description: AkShare 融资融券数据，提供两融余额、杠杆资金监控、两融标的筛选。当用户需要通过 AkShare 获取融资融券数据时使用。
---

# akshare-margin

融资融券数据查询与分析 Skill。提供A股市场融资融券余额、杠杆资金监控、两融标的筛选等功能。

## 功能

- 沪深两市融资融券余额查询
- 个股融资融券明细
- 两融标的股筛选
- 杠杆资金流向分析
- 融资买入/偿还排行

## 使用示例

查询沪深两市融资融券余额：
```bash
python scripts/margin_balance.py
```

查询个股融资融券数据：
```bash
python scripts/margin_stock.py --code 000001
```

查询融资买入排行：
```bash
python scripts/margin_rank.py --type buy --limit 20
```

查询融券卖出排行：
```bash
python scripts/margin_rank.py --type sell --limit 20
```

## 数据来源

- AkShare 融资融券数据接口

## 依赖

- Python 3.8+
- akshare
- pandas
- argparse

## 安装依赖

```bash
pip install akshare pandas
```

## 输出说明

- 融资余额：投资者向券商借钱买入股票的未还金额
- 融券余额：投资者向券商借股卖出的未还金额
- 融资融券余额 = 融资余额 + 融券余额
- 融资买入额：当日融资买入金额
- 融资偿还额：当日融资偿还金额
- 净买入 = 融资买入额 - 融资偿还额

## License

MIT
