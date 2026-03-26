---
description: 微博财经舆情与热搜分析，提供微博财经热搜榜、股票话题热度、舆情情绪分析等。当用户需要查看微博上的财经舆情或热搜时使用。
---

# sentiment-weibo

微博财经舆情与热搜查询 Skill。

## 核心能力

- 微博财经热搜榜
- 微博股票话题热度
- 舆情情绪分析（正面/负面/中性）
- 热点事件追踪

## 使用

```bash
# 查询热搜
python "$SKILLS_ROOT/sentiment-weibo/scripts/weibo_hot.py"

# 查询话题
python "$SKILLS_ROOT/sentiment-weibo/scripts/weibo_topic.py" --keyword 股市
```

## 数据来源

- 微博公开数据

## 相关 Skill

- `sentiment-eastmoney`：东财股吧舆情
- `sentiment-xueqiu`：雪球社区舆情
