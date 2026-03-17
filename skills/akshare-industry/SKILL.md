# AkShare 产业链 Skill

基于 AkShare 的产业链数据获取工具，覆盖申万行业分类、产业链上下游。

## 数据源
- **AkShare**: https://www.akshare.xyz

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `industry_list.py` | 行业列表 | `python industry_list.py` |
| `industry_stocks.py` | 行业成分股 | `python industry_stocks.py 半导体` |
| `industry_chain.py` | 产业链分析 | `python industry_chain.py 新能源` |

## 快速开始

```bash
# 行业列表
python scripts/industry_list.py

# 行业成分股
python scripts/industry_stocks.py 半导体

# 产业链分析
python scripts/industry_chain.py 新能源
```

## 许可证
MIT
