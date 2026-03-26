---
description: 雪球社区舆情与热股榜分析，提供雪球热股榜、情绪监控、个股雪球热度等。当用户需要查看雪球社区舆情或热门股票讨论时使用。
---

# sentiment-xueqiu

雪球财经情绪与热股榜查询 Skill。

## 核心能力

- 雪球热股榜（关注度/讨论度排行）
- 雪球情绪监控
- 个股雪球热度
- 雪球大 V 持仓追踪

## 使用

```bash
# 查询热股榜
python "$SKILLS_ROOT/sentiment-xueqiu/scripts/xueqiu_hot.py"

# 查询个股热度
python "$SKILLS_ROOT/sentiment-xueqiu/scripts/xueqiu_stock.py" --code 000001
```

## 数据来源

- 雪球网公开数据

## 相关 Skill

- `sentiment-eastmoney`：东财股吧舆情
- `sentiment-weibo`：微博财经舆情
