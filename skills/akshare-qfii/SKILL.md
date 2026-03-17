# akshare-qfii

QFII/QDII持仓与外资基金查询 Skill。提供A股市场QFII持仓、QDII基金、外资动向分析等功能。

## 功能

- QFII持仓查询
- QDII基金列表
- QDII基金净值
- 外资持仓统计
- 北向资金关联分析

## 使用示例

查询QFII持仓：
```bash
python scripts/qfii_holdings.py --year 2024 --quarter 3
```

查询QDII基金：
```bash
python scripts/qdii_list.py
```

查询QDII净值：
```bash
python scripts/qdii_nav.py --code 000041
```

## 数据来源

- AkShare QFII/QDII数据接口

## License

MIT
