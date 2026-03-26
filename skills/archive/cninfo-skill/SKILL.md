---
description: ⚠️ DEPRECATED - 东方财富财报数据接口（实际调用 emweb.securities.eastmoney.com），获取 A 股主要财务指标（ZYFXListV2 接口），按 SH/SZ 区分代码前缀。当用户需要查询个股财务指标原始数据时使用。
---

# cninfo-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `cn-stock-data` 或 `akshare-finance` 替代。

## 废弃原因
- 数据源不稳定
- 功能已被其他Skill覆盖

## 替代方案
- 财务数据: 使用 `cn-stock-data` 或 `akshare-finance`
- 公告数据: 使用 `announcement-interpretation-*` 系列 Skill

---

东方财富财务报表数据 JS 封装。

## 核心能力

- 个股主要财务指标查询（营收、净利润、ROE、毛利率等）
- 按市场（SH/SZ）自动适配代码前缀
- 返回标准化 JSON 格式

## 数据源

- 东方财富 emweb.securities.eastmoney.com API

## 使用

```bash
node "$SKILLS_ROOT/cninfo-skill/index.js" --code 600519
```

## 注意

- skill 名称为历史遗留（cninfo），实际数据源为东方财富
- 上层 skill 建议通过 cn-stock-data 统一层获取财务数据
