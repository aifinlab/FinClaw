# AkShare 财经新闻与公告 Skill

基于 AkShare 的财经新闻、公司公告、研报数据获取工具。

## 数据源
- **AkShare**: https://www.akshare.xyz
- **东方财富**: 财经新闻、公告
- **新浪财经**: 实时资讯

## 核心功能

| 脚本 | 功能 | 命令 |
|:---|:---|:---|
| `news_hot.py` | 热点财经新闻 | `python news_hot.py` |
| `news_stock.py` | 个股新闻 | `python news_stock.py 600519` |
| `announcement.py` | 公司公告查询 | `python announcement.py 600519` |
| `research_report.py` | 券商研报 | `python research_report.py 600519` |
| `news_sentiment.py` | 新闻情感分析 | `python news_sentiment.py 600519` |
| `news_monitor.py` | 关键词监控 | `python news_monitor.py 回购` |
| `earnings_preview.py` | 业绩预告 | `python earnings_preview.py` |

## 公告类型

| 类型 | 说明 | 重要性 |
|:---|:---|:---:|
| 业绩预告 | 季度/年度业绩预测 | ⭐⭐⭐ |
| 业绩快报 | 业绩快报披露 | ⭐⭐⭐ |
| 增减持 | 股东增减持计划 | ⭐⭐⭐ |
| 回购 | 股票回购公告 | ⭐⭐⭐ |
| 股权激励 | 员工持股/期权激励 | ⭐⭐ |
| 重大合同 | 重大订单/合同 | ⭐⭐⭐ |
| 并购重组 | 并购/重组/资产注入 | ⭐⭐⭐ |
| 定向增发 | 定增方案/进展 | ⭐⭐ |

## 快速开始

```bash
# 安装依赖
pip install akshare pandas jieba

# 获取热点新闻
python scripts/news_hot.py

# 获取个股公告
python scripts/announcement.py 600519

# 获取研报数据
python scripts/research_report.py 300750

# 监控关键词
python scripts/news_monitor.py 增持
```

## 情感分析

基于新闻标题的情感倾向判断：
- **积极**: 上涨、突破、超预期、订单大增、回购
- **消极**: 下跌、跌破、亏损、减持、解禁、处罚
- **中性**: 公告、分红、转股、会议

## 关键词预警

支持监控的关键词类型：
- 业绩类: 预增、扭亏、超预期
- 资金类: 增持、回购、员工持股
- 业务类: 订单、中标、合同
- 风险类: 减持、解禁、处罚、诉讼

## 许可证
MIT
