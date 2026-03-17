# AkShare 资金流向 Skill

基于 AkShare 的资金流向数据获取工具，追踪主力资金、散户资金、北向资金动向。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **东方财富**: 资金流向数据

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `capital_flow.py` | 个股资金流向 | `python capital_flow.py 600519` |
| `capital_board.py` | 板块资金流向 | `python capital_board.py` |
| `capital_north.py` | 北向资金明细 | `python capital_north.py` |
| `capital_main.py` | 主力资金排行 | `python capital_main.py` |

## 资金流向分类

| 类型 | 说明 |
|:---|:---|
| 超大单 | >100万股，机构主力 |
| 大单 | 20-100万股，大资金 |
| 中单 | 4-20万股，中等资金 |
| 小单 | <4万股，散户资金 |

## 快速开始

```bash
# 获取个股资金流向
python scripts/capital_flow.py 600519

# 获取板块资金流向
python scripts/capital_board.py

# 获取北向资金
python scripts/capital_north.py
```

## 许可证
MIT
