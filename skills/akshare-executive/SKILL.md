# akshare-executive

高管持股与增减持查询 Skill。提供A股市场高管持股变动、增减持记录、薪酬分析等功能。

## 功能

- 高管增减持查询
- 个股高管持股变动
- 高管增持排行
- 高管减持排行
- 董监高持股统计

## 使用示例

查询高管增减持：
```bash
python scripts/executive_change.py --limit 30
```

查询个股高管变动：
```bash
python scripts/executive_stock.py --code 000001
```

增持排行：
```bash
python scripts/executive_buy.py
```

减持排行：
```bash
python scripts/executive_sell.py
```

## 数据来源

- AkShare 高管持股数据接口

## License

MIT
