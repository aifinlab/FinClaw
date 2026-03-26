---
description: 腾讯财经债券行情接口，通过腾讯行情 API 获取债券实时行情数据。当用户需要查询债券实时价格（腾讯源）时使用。
---

# tencent-bond-skill

腾讯财经债券行情 JS 封装。

## 核心能力

- 债券实时行情查询
- 支持 SH/SZ 前缀代码
- 解析腾讯私有文本格式

## 数据源

- 腾讯财经 qt.gtimg.cn API

## 使用

```bash
node "$SKILLS_ROOT/tencent-bond-skill/index.js" --code sh019666
```

## 相关 Skill

- `eastmoney-bond-skill`：东方财富债券数据
- `akshare-bond`：AkShare 债券数据接口
