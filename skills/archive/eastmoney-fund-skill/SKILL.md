---
description: ⚠️ DEPRECATED - 东方财富基金数据接口，提供基金列表、排行、净值、详情等数据。当用户需要查询基金排行榜、基金筛选列表时使用。
---

# eastmoney-fund-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `akshare-fund` 替代。

## 废弃原因
- 数据源不稳定，经常变动接口
- 功能已被 `akshare-fund` 覆盖
- 缺乏官方API支持

## 替代方案
- 基金排行: `akshare-fund`
- 基金筛选: `a-share-stock-screen` + `fund-product-tag-maintenance-assistant`
- 基金详情: `fund-manager-profile-*` 系列

---

东方财富基金数据 JS 封装。

## 核心能力

- 基金列表与筛选
- 基金排行榜
- 基金净值查询
- 基金详情数据

## 数据源

- 东方财富 datacenter-web.eastmoney.com API

## 使用

```bash
node "$SKILLS_ROOT/eastmoney-fund-skill/index.js"
```

## 相关 Skill

- `eastmoney-fund-daily`：单只基金详情（天天基金源）- 同样已废弃
- `akshare-fund`：AkShare 基金数据接口（推荐）
