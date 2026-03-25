---
name: securities-rating-analyzer
description: 券商研报评级分析工具。接入东方财富研报数据，实现研报获取、解析、评分功能。支持个股研报分析、机构研报搜索、头部券商对比。使用 AkShare 实时数据源。适用于投资决策辅助、券商研究能力评估、研报情绪分析。
requirements:
  - akshare
---

# 券商研报评级分析器

## 功能

- **研报数据获取**: 接入东方财富研报数据 (AkShare: stock_research_report_em)
- **研报解析**: 自动解析评级、盈利预测、机构信息等
- **智能评分**: 基于研报覆盖度、评级分布、一致性计算综合评分
- **个股分析**: 支持任意A股代码的研报分析
- **机构搜索**: 按券商机构名称搜索研报
- **头部券商分析**: 内置头部券商列表，一键对比分析

## 数据源

- **东方财富网** (data.eastmoney.com)
- **AkShare** 金融数据接口库

## 安装依赖

```bash
pip install akshare
```

## 使用方法

### 命令行

```bash
# 分析单只股票研报
python main.py --symbol 000001

# 分析头部券商
python main.py --all

# 按机构搜索研报
python main.py --institution "中信证券"
```

### Python API

```python
from scripts.main import SecuritiesRatingAnalyzer

analyzer = SecuritiesRatingAnalyzer()

# 获取个股研报
reports = analyzer.get_stock_reports('000001')

# 分析评级数据
analysis = analyzer.analyze_ratings(reports)

# 获取完整分析结果
result = analyzer.get_brokerage_research_analysis(symbol='000001')
```

## 输出字段说明

### 分析结果 (Analysis)

| 字段 | 说明 |
|------|------|
| total_reports | 研报总数 |
| rating_distribution | 评级分布统计 |
| latest_report | 最新研报信息 |
| buy_ratio | 买入/推荐评级比例 |
| neutral_ratio | 中性评级比例 |
| sell_ratio | 减持/卖出评级比例 |
| predictions | 盈利预测平均值 (EPS/PE) |
| composite_score | 综合评分 (0-100) |
| recommendation | 投资建议 |

### 综合评分算法

综合评分基于以下维度计算:

1. **评级分布权重** (基础分): 买入评级越多，得分越高
2. **研报覆盖度** (加分项): 研报数量越多，覆盖度越高
3. **观点一致性** (加分项): 买入比例高且无卖出评级，一致性得分高
4. **数据新鲜度** (加分项): 最近1个月内有研报额外加分

### 评级映射

| 东财评级 | 权重 |
|----------|------|
| 买入/强烈推荐 | 5 |
| 增持/推荐 | 4 |
| 中性/谨慎推荐 | 3 |
| 减持 | 2 |
| 卖出/回避 | 1 |

## 内置头部券商列表

| 代码 | 名称 |
|------|------|
| 600030 | 中信证券 |
| 601688 | 华泰证券 |
| 600837 | 海通证券 |
| 601211 | 国泰君安 |
| 600999 | 招商证券 |
| 000776 | 广发证券 |
| 601995 | 中金公司 |
| 601066 | 中信建投 |
| 600958 | 东方证券 |
| 601377 | 兴业证券 |
| ... | ... |

## 示例输出

```json
{
  "query_time": "2026-03-25 09:00:36",
  "symbol": "000001",
  "data_source": "东方财富研报数据 (AkShare)",
  "analysis": {
    "total_reports": 225,
    "rating_distribution": {
      "买入": 136,
      "增持": 66,
      "中性": 8
    },
    "latest_report": {
      "rating": "中性",
      "institution": "国信证券",
      "date": "2026-03-22"
    },
    "ratios": {
      "buy_ratio": "60.44%",
      "neutral_ratio": "3.56%",
      "sell_ratio": "0.0%"
    },
    "predictions": {
      "avg_eps_2025": 3.08,
      "avg_pe_2025": 3.96,
      "avg_eps_2026": 2.47,
      "avg_pe_2026": 4.55
    },
    "composite_score": 100,
    "recommendation": "强烈看好 - 机构一致看多，研报覆盖充分"
  }
}
```

## 注意事项

1. 数据来源于东方财富公开研报，可能存在延迟
2. 研报评级仅供参考，不构成投资建议
3. 需要网络连接才能获取实时数据
4. 首次运行可能需要下载 AkShare 依赖
