---
description: ⚠️ DEPRECATED - 东方财富债券数据接口，提供国债收益率曲线、可转债行情等债券市场数据。当用户需要查询国债收益率、可转债价格等债券数据时使用。
---

# eastmoney-bond-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `akshare-bond` 或 `tencent-bond-skill` 替代。

## 废弃原因
- 数据源不稳定，经常变动接口
- 功能已被 `akshare-bond` 覆盖
- 缺乏官方API支持

## 替代方案
- 债券数据: `akshare-bond`
- 国债收益率: `akshare-macro` 或 `fred-data`
- 可转债: `a-share-convertible-bond`

---

东方财富债券数据 JS 封装。

## 核心能力

- 国债收益率数据查询
- 可转债实时行情
- 债券市场数据统一封装

## 数据源

- 东方财富 datacenter-web.eastmoney.com API

## 使用

```bash
node "$SKILLS_ROOT/eastmoney-bond-skill/index.js"
```
