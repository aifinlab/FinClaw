---
description: ⚠️ DEPRECATED - 同花顺 iFinD 专业金融数据 HTTP API 底层封装，是其他 ths-* skill 的共用底座。当需要直接调用同花顺 iFinD API 时使用。
---

# ths-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。原因：同花顺 API Token 已过期，且获取新 Token 流程复杂。

## 废弃原因
- THS_ACCESS_TOKEN 已过期 (2026-04-01)
- 获取新 Token 需要企业资质认证
- 已有更稳定的替代数据源

## 替代方案
- A股数据: `akshare-stock`, `akshare-finance`
- 宏观数据: `akshare-macro`, `fred-data`
- 实时行情: `tushare-pro`, `efinance-data`

---

同花顺 iFinD 金融数据底层 JS 封装。

## 核心能力

- 同花顺 iFinD HTTP API 统一调用
- ACCESS_TOKEN 认证管理（从 .env 读取）
- 是 ths-edb-skill、insurance-skill 等的底层依赖

## 配置

```bash
# .env
THS_ACCESS_TOKEN=your_token_here
```

## 使用

```javascript
const ths = require("$SKILLS_ROOT/ths-skill/index.js");
// 调用 iFinD API
```

## 注意

- 需要同花顺 iFinD 专业版账号
- TOKEN 配置在项目根目录 .env 文件中
