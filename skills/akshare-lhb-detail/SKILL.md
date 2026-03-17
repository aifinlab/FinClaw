# akshare-lhb-detail

龙虎榜数据查询与分析 Skill。提供A股市场龙虎榜营业部追踪、游资图谱、机构席位分析等功能。

## 功能

- 每日龙虎榜数据查询
- 营业部追踪（游资动向）
- 机构专用席位分析
- 龙虎榜个股筛选
- 游资图谱生成

## 使用示例

查询今日龙虎榜：
```bash
python scripts/lhb_daily.py
```

查询个股龙虎榜历史：
```bash
python scripts/lhb_stock.py --code 000001
```

追踪营业部：
```bash
python scripts/lhb_dealer.py --name "中信证券上海溧阳路"
```

查询机构席位动向：
```bash
python scripts/lhb_institution.py --days 30
```

## 数据来源

- AkShare 龙虎榜数据接口

## 依赖

- Python 3.8+
- akshare
- pandas
- argparse

## 安装依赖

```bash
pip install akshare pandas
```

## 龙虎榜说明

- 龙虎榜：交易所公布的当日涨幅/跌幅/换手率异常的股票交易明细
- 上榜条件：日涨跌幅偏离值达±7%、日振幅达15%、换手率超20%等
- 营业部：券商在交易所的交易席位，知名游资有固定席位
- 机构席位：公募基金、保险、QFII等机构投资者专用席位

## License

MIT
