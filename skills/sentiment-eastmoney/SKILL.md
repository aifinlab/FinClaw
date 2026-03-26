---
description: 东方财富股吧舆情与热度分析，提供股吧热度排行、个股情绪指标、散户情绪监控等。当用户需要查看东财股吧热度或散户情绪时使用。
---

# sentiment-eastmoney

东方财富情绪与股吧热度查询 Skill。

## 核心能力

- 东财股吧热度排行
- 个股情绪指标（多空比/情绪评分）
- 散户情绪监控
- 情绪指数计算

## 使用

```bash
# 查询热度排行
python "$SKILLS_ROOT/sentiment-eastmoney/scripts/eastmoney_hot.py"

# 查询个股情绪
python "$SKILLS_ROOT/sentiment-eastmoney/scripts/eastmoney_sentiment.py" --code 000001
```

## 数据来源

- 东方财富股吧公开数据

## 相关 Skill

- `sentiment-weibo`：微博财经舆情
- `sentiment-xueqiu`：雪球社区舆情
- `a-share-sentiment`：多源情绪综合研判
