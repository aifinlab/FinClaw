---
description: ⚠️ DEPRECATED - 东方财富综合数据接口，提供 A 股基本信息、财务三表（资产负债/利润/现金流）、主要财务指标及公告查询。当用户需要个股财务三表或公告原始数据时使用。
---

# eastmoney-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `cn-stock-data` 或 `akshare-*` 系列替代。

## 废弃原因
- 数据源不稳定，经常变动接口
- 功能已被 `akshare-stock`、`akshare-finance` 等覆盖
- 缺乏官方API支持

## 替代方案
- 股票数据: `akshare-stock`, `tushare-pro`
- 财务数据: `akshare-finance`, `cn-stock-data`
- 公告数据: `announcement-interpretation-*` 系列

---

东方财富综合金融数据 JS 封装。

## 核心能力

- 股票基本信息查询
- 财务三表：资产负债表、利润表、现金流量表
- 主要财务指标
- 最新公告查询

## 数据源

- 东方财富公开免费 API

## 使用

```bash
node "$SKILLS_ROOT/eastmoney-skill/index.js" --code 600519
```
