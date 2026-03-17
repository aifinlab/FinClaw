# akshare-fof

FOF基金与养老目标基金查询 Skill。提供A股市场FOF基金净值、业绩排行、持仓分析等功能。

## 功能

- FOF基金列表查询
- FOF基金净值查询
- FOF业绩排行
- FOF持仓穿透分析
- 养老目标基金专题

## 使用示例

查询FOF基金列表：
```bash
python scripts/fof_list.py
```

查询FOF净值：
```bash
python scripts/fof_nav.py --code 006308
```

FOF业绩排行：
```bash
python scripts/fof_rank.py --period 1y
```

养老目标基金：
```bash
python scripts/fof_pension.py
```

## 数据来源

- AkShare FOF基金数据接口

## License

MIT
