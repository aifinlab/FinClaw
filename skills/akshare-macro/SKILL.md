# AkShare 宏观经济数据 Skill

基于 AkShare 的宏观经济数据获取工具，覆盖GDP、CPI、PPI、M2、PMI、利率、汇率等核心指标。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **费用**: 完全免费
- **覆盖**: 中国及全球主要经济体宏观数据

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `macro_gdp.py` | GDP季度/年度数据 | `python macro_gdp.py` |
| `macro_cpi.py` | CPI通胀数据 | `python macro_cpi.py` |
| `macro_ppi.py` | PPI生产者物价 | `python macro_ppi.py` |
| `macro_m2.py` | M2货币供应量 | `python macro_m2.py` |
| `macro_pmi.py` | 制造业PMI | `python macro_pmi.py` |
| `macro_rate.py` | LPR利率/人民币汇率 | `python macro_rate.py` |
| `macro_summary.py` | 宏观概览仪表盘 | `python macro_summary.py` |

## 快速开始

```bash
# 安装依赖
pip install akshare pandas

# 获取GDP数据
python scripts/macro_gdp.py

# 获取宏观概览
python scripts/macro_summary.py
```

## 数据字段说明

### GDP数据
- `quarter`: 季度
- `gdp`: GDP累计值(亿元)
- `gdp_yoy`: GDP同比增长(%)
- `gdp_qoq`: GDP环比增长(%)

### CPI数据
- `date`: 日期
- `cpi`: CPI同比(%)
- `cpi_mom`: CPI环比(%)
- `core_cpi`: 核心CPI(%)

### M2数据
- `date`: 日期
- `m2`: M2余额(万亿元)
- `m2_yoy`: M2同比增长(%)
- `m1_yoy`: M1同比增长(%)

## 经济周期判断

基于GDP+CPI+PMI综合判断经济周期阶段：
- **复苏期**: GDP↑ + CPI↓ + PMI>50
- **过热期**: GDP↑ + CPI↑ + PMI>50
- **滞胀期**: GDP↓ + CPI↑ + PMI<50
- **衰退期**: GDP↓ + CPI↓ + PMI<50

## 许可证
MIT
