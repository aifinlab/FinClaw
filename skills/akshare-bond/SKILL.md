# AkShare 债券数据 Skill

基于 AkShare 的债券数据获取工具，覆盖国债、企业债、可转债。

## 数据源
- **AkShare**: https://www.akshare.xyz

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `bond_quote.py` | 债券行情 | `python bond_quote.py` |
| `bond_convertible.py` | 可转债数据 | `python bond_convertible.py` |
| `bond_yield.py` | 收益率曲线 | `python bond_yield.py` |

## 快速开始

```bash
# 获取债券行情
python scripts/bond_quote.py

# 获取可转债数据
python scripts/bond_convertible.py

# 获取收益率曲线
python scripts/bond_yield.py
```

## 许可证
MIT
