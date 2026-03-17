# akshare-pledge

股权质押数据查询与风险预警 Skill。提供A股市场股权质押比例查询、质押风险预警、解禁股提醒等功能。

## 功能

- 个股股权质押比例查询
- 高质押比例股票筛选（风险预警）
- 质押方统计
- 解禁股查询
- 质押到期提醒

## 使用示例

查询个股质押情况：
```bash
python scripts/pledge_stock.py --code 000001
```

查询高质押风险股票：
```bash
python scripts/pledge_high.py --limit 50
```

查询解禁股：
```bash
python scripts/pledge_unlock.py --days 30
```

## 数据来源

- AkShare 股权质押数据接口

## 依赖

- Python 3.8+
- akshare
- pandas

## License

MIT
