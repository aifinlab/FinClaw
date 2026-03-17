# akshare-reits

公募REITs与基础设施查询 Skill。提供A股市场REITs行情、收益分析、资产类型筛选等功能。

## 功能

- REITs基金列表
- REITs行情查询
- REITs收益分析
- 按资产类型筛选（产业园/仓储物流/高速公路等）
- REITs分红统计

## 使用示例

查询REITs列表：
```bash
python scripts/reits_list.py
```

查询REITs行情：
```bash
python scripts/reits_quote.py
```

按类型筛选：
```bash
python scripts/reits_type.py --type 产业园
```

## 数据来源

- AkShare REITs数据接口

## License

MIT
