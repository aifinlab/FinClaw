# AkShare 股东数据 Skill

基于 AkShare 的股东数据获取工具，覆盖股东增减持、机构持仓、筹码分布。

## 数据源
- **AkShare**: https://www.akshare.xyz

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `holders_change.py` | 股东增减持 | `python holders_change.py 600519` |
| `holders_institutional.py` | 机构持仓 | `python holders_institutional.py 600519` |
| `holders_chips.py` | 筹码分布 | `python holders_chips.py 600519` |

## 快速开始

```bash
# 股东增减持
python scripts/holders_change.py 600519

# 机构持仓
python scripts/holders_institutional.py 600519

# 筹码分布
python scripts/holders_chips.py 600519
```

## 许可证
MIT
