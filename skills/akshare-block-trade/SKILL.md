# akshare-block-trade

大宗交易数据查询与分析 Skill。提供A股市场大宗交易明细、机构席位追踪、折溢价分析等功能。

## 功能

- 每日大宗交易数据查询
- 机构专用席位大宗交易追踪
- 大宗交易折溢价分析
- 个股大宗交易历史
- 营业部大宗交易统计

## 使用示例

查询今日大宗交易：
```bash
python scripts/block_daily.py
```

查询个股大宗交易：
```bash
python scripts/block_stock.py --code 000001
```

查询机构大宗交易：
```bash
python scripts/block_institution.py --days 30
```

折溢价分析：
```bash
python scripts/block_premium.py
```

## 数据来源

- AkShare 大宗交易数据接口

## 依赖

- Python 3.8+
- akshare
- pandas
- argparse

## 安装依赖

```bash
pip install akshare pandas
```

## 大宗交易说明

- 大宗交易：单笔交易数量或金额达到一定标准的证券买卖
- 沪市标准：A股单笔≥30万股或≥200万元；B股≥30万股或≥20万美元
- 深市标准：A股单笔≥30万股或≥300万元；B股≥3万股或≥20万港币
- 折溢价：大宗交易成交价相对于当日收盘价的涨跌幅度

## License

MIT
