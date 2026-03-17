# akshare-alerts

智能预警系统 Skill。提供A股市场价格预警、成交量预警、公告预警、技术指标预警等功能。

## 功能

- 价格预警（突破/跌破设定价位）
- 成交量异常预警
- 涨跌停预警
- 公告预警
- 技术指标预警（金叉/死叉）

## 使用示例

设置价格预警：
```bash
python scripts/alert_price.py --code 000001 --above 15.0
```

设置跌幅预警：
```bash
python scripts/alert_price.py --code 000001 --below 12.0
```

涨跌停预警：
```bash
python scripts/alert_limit.py
```

成交量异常：
```bash
python scripts/alert_volume.py --threshold 5
```

## 数据来源

- AkShare 实时行情数据接口

## 依赖

- Python 3.8+
- akshare
- pandas

## License

MIT
