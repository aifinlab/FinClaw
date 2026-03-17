# fund-backtest

基金组合回测与定投分析 Skill。提供基金组合回测、定投收益计算、绩效分析等功能。

## 功能

- 基金组合回测
- 定投收益计算
- 基金对比分析
- 风险指标计算
- 定投计划生成

## 使用示例

基金回测：
```bash
python scripts/fund_backtest.py --code 006308 --start 2023-01-01 --end 2024-01-01
```

定投计算：
```bash
python scripts/fund_dca.py --code 006308 --amount 1000 --period monthly --years 3
```

基金对比：
```bash
python scripts/fund_compare.py --codes 006308,000001,110022
```

## 数据来源

- AkShare 基金历史净值数据

## License

MIT
