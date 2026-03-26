---
description: ⚠️ DEPRECATED - 外部第三方 skill 集成目录，提供 Stock Analysis（雅虎财经/美股）、Tavily 搜索、Firecrawl 网页爬取等安装配置。当需要安装外部数据增强 skill 时使用。
---

# external (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。外部集成已分散到各独立 Skill 中。

## 废弃原因
- 集中式外部集成维护困难
- 各外部服务已独立成 Skill
- 安装脚本已过时

## 替代方案
- 美股数据: `yfinance-global`
- 搜索: `exa-web-search-free`, `multi-search-engine`
- 网页爬取: `agent-browser`

---

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
