---
description: 外部第三方 skill 集成目录，提供 Stock Analysis（雅虎财经/美股）、Tavily 搜索、Firecrawl 网页爬取等安装配置。当需要安装外部数据增强 skill 时使用。
---

# external

外部第三方 skill 集成目录。

## 可安装的外部 skill

| Skill | 来源 | 功能 |
|-------|------|------|
| Stock Analysis | 雅虎财经 | 美股行情与基本面 |
| Tavily | Tavily API | 网络搜索 |
| Summarize | 内置 | 内容摘要 |
| Firecrawl | Firecrawl API | 网页爬取 |

## 安装

```bash
# 方案一：一键安装
bash "$SKILLS_ROOT/external/install-scheme1.sh"
```

## 定位

FinClaw 核心功能的数据增强层，提供非金融类辅助能力。
