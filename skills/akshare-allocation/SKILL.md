# akshare-allocation

基金资产配置与行业配置查询 Skill。提供A股市场基金资产配置结构、行业分布、重仓股分析等功能。

## 功能

- 基金资产配置查询（股票/债券/现金）
- 行业配置分布
- 重仓股分析
- 持仓变动追踪
- 债券持仓分析

## 使用示例

查询资产配置：
```bash
python scripts/allocation_asset.py --code 006308
```

查询行业配置：
```bash
python scripts/allocation_sector.py --code 006308
```

查询重仓股：
```bash
python scripts/allocation_holdings.py --code 006308
```

## 数据来源

- AkShare 基金持仓数据接口

## License

MIT
