# AkShare 财报数据 Skill

基于 AkShare 的财报数据获取工具，覆盖三大表、财务指标分析。

## 数据源
- **AkShare**: https://www.akshare.xyz

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `financial_report.py` | 三大表数据 | `python financial_report.py 600519` |
| `financial_indicator.py` | 财务指标 | `python financial_indicator.py 600519` |
| `financial_dupont.py` | 杜邦分析 | `python financial_dupont.py 600519` |

## 财务指标

| 指标 | 说明 |
|:---|:---|
| ROE | 净资产收益率 |
| ROA | 总资产收益率 |
| 毛利率 | 毛利润/营业收入 |
| 净利率 | 净利润/营业收入 |
| 资产负债率 | 负债/资产 |
| 流动比率 | 流动资产/流动负债 |

## 快速开始

```bash
# 获取三大表
python scripts/financial_report.py 600519

# 获取财务指标
python scripts/financial_indicator.py 600519

# 杜邦分析
python scripts/financial_dupont.py 600519
```

## 许可证
MIT
