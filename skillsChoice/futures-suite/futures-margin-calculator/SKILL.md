---
name: futures-margin-calculator
description: 期货保证金计算工具。计算各期货品种的交易所保证金、期货公司保证金、开仓所需资金。支持不同交易所、不同品种的保证金率查询。使用AkShare实时数据、交易所官方保证金标准。适用于资金管理、风险控制、交易策略制定。
---

# 期货保证金计算器

## 功能

- 交易所保证金率实时查询（接入AkShare）
- 期货公司保证金率设置
- 开仓资金计算
- 维持保证金监控
- 不同品种保证金对比
- 多交易所数据支持

## 数据源

- **AkShare实时数据**: `futures_comm_info()` 接口获取实时保证金率、手续费数据
- 支持交易所: 上期所、大商所、郑商所、能源中心、中金所、广期所
- 数据包括: 交易所保证金率(买开/卖开)、每手保证金金额、实时价格

## 核心指标

| 指标 | 说明 |
|------|------|
| 交易所保证金率 | 交易所要求的最低保证金比例（实时） |
| 期货公司保证金率 | 期货公司实际收取的保证金比例 |
| 合约价值 | 合约价格 × 合约乘数 |
| 保证金金额 | 合约价值 × 保证金率 |

## 使用方法

```bash
# 计算单个合约保证金
python main.py --symbol RB2505 --price 3200 --lots 2

# 使用AkShare实时价格（不指定--price）
python main.py --symbol RB2505 --lots 1

# 做空保证金计算
python main.py --symbol RB2505 --price 3200 --direction short

# 列出所有品种保证金率
python main.py --list

# 列出指定交易所品种
python main.py --list --exchange SHFE

# 对比多个合约保证金
python main.py --compare RB2505,HC2505,I2505 --lots 1
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| --symbol | 合约代码 | RB2505, CU2506 |
| --price | 合约价格（可选，默认使用AkShare实时价） | 3500 |
| --lots | 手数 | 2 |
| --multiplier | 期货公司保证金倍数 | 1.2 |
| --direction | 交易方向(long/short) | long |
| --list | 列出保证金率 | - |
| --exchange | 指定交易所过滤 | SHFE/DCE/CZCE/INE/CFFEX/GFEX |
| --compare | 对比多个合约 | RB2505,HC2505 |

## 更新日志

- 2025-03-25: 接入AkShare实时数据源，替换静态配置
