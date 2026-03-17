# akshare-manager

基金经理业绩与任期分析 Skill。提供A股市场基金经理业绩排行、任期统计、在管基金查询等功能。

## 功能

- 基金经理业绩排行
- 基金经理在管基金
- 基金经理任期统计
- 基金经理换手率分析
- 明星基金经理追踪

## 使用示例

查询基金经理排行：
```bash
python scripts/manager_rank.py --period 1y
```

查询基金经理详情：
```bash
python scripts/manager_detail.py --name 张坤
```

查询在管基金：
```bash
python scripts/manager_funds.py --name 刘彦春
```

## 数据来源

- AkShare 基金经理数据接口

## License

MIT
