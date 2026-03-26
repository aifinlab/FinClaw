---
description: ⚠️ DEPRECATED - 保险行业行情数据，获取主要保险股（平安/人寿/太保/人保等）及保险行业 ETF 实时行情。当用户需要查看保险板块行情时使用。
---

# insurance-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `akshare-stock` 或 `ths-skill` 替代。

## 废弃原因
- 依赖的 ths-skill token 已过期
- 功能已被 `akshare-stock` 覆盖
- 数据更新不及时

## 替代方案
- 保险股行情: `akshare-stock`
- 行业数据: `ths-skill` (需配置有效token)

---

保险行业行情数据 JS 封装。

## 核心能力

- 主要保险股实时行情（平安、人寿、太保、人保等）
- 保险行业 ETF 行情
- 板块整体涨跌

## 依赖

- ths-skill（同花顺底层接口）
- 腾讯财经行情 API

## 使用

```bash
node "$SKILLS_ROOT/insurance-skill/index.js"
```
