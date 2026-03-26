---
description: ⚠️ DEPRECATED - 天天基金网基金详情数据，获取基金实时估值、历史净值、持仓结构等。当用户需要查询单只基金的净值走势、持仓明细时使用。
---

# eastmoney-fund-daily (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `akshare-fund` 或 `tushare-pro` 替代。

## 废弃原因
- 数据源不稳定
- 接口经常变动
- 功能已被 `akshare-fund` 覆盖

## 替代方案
- 基金数据: `akshare-fund`
- 基金详情: `fund-manager-profile-*` 系列
- 持仓分析: `a-share-fund-holding`

---

天天基金网基金详情数据 JS 封装。

## 核心能力

- 基金实时估值查询
- 历史净值数据
- 持仓结构（股票/债券/行业）
- 基金经理信息

## 数据源

- 天天基金网 fund.eastmoney.com/pingzhongdata API

## 使用

```bash
node "$SKILLS_ROOT/eastmoney-fund-daily/index.js" --fund 110011
```
