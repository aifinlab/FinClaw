---
description: ⚠️ DEPRECATED - 技术指标计算工具库（纯本地计算），提供 MA/MACD/KDJ/RSI/BOLL 五类常用技术指标。当用户需要对价格序列计算技术指标时使用。
---

# technical-skill (已废弃)

⚠️ **状态: DEPRECATED (2026-03-25)**

> 此 Skill 已废弃，不再维护。建议使用 `akshare-index` 或专业量化库替代。

## 废弃原因
- 功能简单，已被更专业的量化库覆盖
- 建议使用 `akshare` 内置的技术指标功能
- 维护成本高，使用率低

## 替代方案
- Python: `talib`, `pandas-ta`
- JavaScript: `technicalindicators`
- AkShare: `akshare-index` 模块

---

A 股技术指标计算工具库（JS 版）。

## 核心能力

- MA（移动平均线）
- MACD（指数平滑异同移动平均线）
- KDJ（随机指标）
- RSI（相对强弱指标）
- BOLL（布林带）

## 特点

- 纯本地计算，无外部 API 依赖
- 输入价格数组，输出指标值
- 支持 K 线数据格式化

## 使用

```javascript
const { calcMA, calcMACD, calcKDJ, calcRSI, calcBOLL } = require("$SKILLS_ROOT/technical-skill/index.js");
```
