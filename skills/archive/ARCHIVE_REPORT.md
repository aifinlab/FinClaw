# FinClaw Skill 归档清单报告

**归档日期**: 2025-03-25  
**归档执行**: OpenClaw Agent  
**归档位置**: `finclaw/skills/archive/`

---

## 一、归档概述

本次归档共涉及 **11 个废弃 Skill**，这些 Skills 因接口变更、功能合并、长期缺乏维护等原因已不再推荐使用。

---

## 二、已归档 Skill 清单

| 序号 | Skill 名称 | 原分类 | 大小 | 归档原因 | 推荐替代方案 |
|:---:|:---|:---|---:|:---|:---|
| 1 | `cninfo-skill` | 第三方数据源 | 20K | 巨潮接口变更 | `cn-stock-data` 统一数据层 |
| 2 | `eastmoney-skill` | 第三方数据源 | 20K | 东财接口变更 | `cn-stock-data` 统一数据层 |
| 3 | `eastmoney-bond-skill` | 第三方数据源 | 16K | 东财接口变更 | `akshare-bond` |
| 4 | `eastmoney-fund-daily` | 第三方数据源 | 16K | 东财接口变更 | `akshare-fund` |
| 5 | `eastmoney-fund-skill` | 第三方数据源 | 16K | 东财接口变更 | `akshare-fund` |
| 6 | `external` | 其他 | 60K | 架构调整 | 内建数据源 |
| 7 | `fastgpt-skill` | 其他 | 16K | 架构调整 | 系统内建 LLM 能力 |
| 8 | `insurance-skill` | 保险业务 | 24K | 功能拆分细化 | 细分保险 Skills |
| 9 | `technical-skill` | 量化工具 | 32K | 功能合并 | `a-share-technical` |
| 10 | `ths-skill` | 第三方数据源 | 32K | 同花顺接口变更 | `cn-stock-data` 统一数据层 |
| 11 | `ths-edb-skill` | 第三方数据源 | 24K | 同花顺接口变更 | `akshare-macro` |

**总计**: 11 个 Skills, 约 296K

---

## 三、归档原因分类

### 1. 第三方数据源接口变更（7个）
- `cninfo-skill`
- `eastmoney-skill`
- `eastmoney-bond-skill`
- `eastmoney-fund-daily`
- `eastmoney-fund-skill`
- `ths-skill`
- `ths-edb-skill`

**说明**: 这些 Skill 依赖的第三方数据接口（东财、同花顺、巨潮）发生变更或限制，导致原有实现无法正常工作。已被 `cn-stock-data` 统一数据层或 AkShare 相关 Skill 替代。

### 2. 架构调整（2个）
- `external`
- `fastgpt-skill`

**说明**: 随着系统架构演进，这些 Skill 的功能已被内建能力吸收。

### 3. 功能拆分/合并（2个）
- `insurance-skill` → 拆分为 21 个细分保险 Skills
- `technical-skill` → 合并至 `a-share-technical`

---

## 四、目录结构

```
finclaw/skills/
├── archive/                     # 📦 归档目录
│   ├── cninfo-skill/            # 巨潮资讯数据
│   │   └── ...
│   ├── eastmoney-skill/         # 东方财富综合数据
│   │   └── ...
│   ├── eastmoney-bond-skill/    # 东财债券数据
│   │   └── ...
│   ├── eastmoney-fund-daily/    # 东财基金每日净值
│   │   └── ...
│   ├── eastmoney-fund-skill/    # 东财基金数据
│   │   └── ...
│   ├── external/                # 外部接口
│   │   └── ...
│   ├── fastgpt-skill/           # FastGPT集成
│   │   └── ...
│   ├── insurance-skill/         # 保险综合
│   │   └── ...
│   ├── technical-skill/         # 技术指标计算
│   │   └── ...
│   ├── ths-skill/               # 同花顺数据接口
│   │   └── ...
│   └── ths-edb-skill/           # 同花顺经济数据库
│       └── ...
│
└── [其他活跃 Skills...]         # 正常使用的 Skills
```

---

## 五、使用建议

### 1. 不推荐恢复使用
- 归档 Skills 不再维护，不保证可用性
- 可能存在接口失效、数据错误等问题

### 2. 迁移至替代方案
| 原有 Skill | 推荐替代方案 |
|:---|:---|
| 东财/同花顺/巨潮数据源 | `cn-stock-data` 统一数据层 |
| 债券数据 | `akshare-bond` |
| 基金数据 | `akshare-fund` |
| 宏观数据 | `akshare-macro` |
| 技术指标 | `a-share-technical` |
| 保险分析 | 21个细分保险 Skills |

### 3. 如确需恢复
```bash
# 从 archive 复制回原位置
cp -r finclaw/skills/archive/eastmoney-skill finclaw/skills/
```

---

## 六、后续维护

1. **定期清理**: 建议每季度检查一次 archive 目录
2. **文档同步**: README 中已标注 [已归档] 状态
3. **替代方案维护**: 确保替代 Skills 的功能完整性

---

## 七、附录：详细文件列表

```
archive/
├── cninfo-skill/
│   └── SKILL.md
├── eastmoney-bond-skill/
│   └── SKILL.md
├── eastmoney-fund-daily/
│   └── SKILL.md
├── eastmoney-fund-skill/
│   └── SKILL.md
├── eastmoney-skill/
│   ├── __init__.py
│   ├── config.py
│   ├── eastmoney_service.py
│   └── SKILL.md
├── external/
│   ├── external_service.py
│   ├── market_data.py
│   ├── news_sentiment.py
│   ├── __init__.py
│   └── SKILL.md
├── fastgpt-skill/
│   └── SKILL.md
├── insurance-skill/
│   ├── __init__.py
│   ├── insurance_service.py
│   └── SKILL.md
├── technical-skill/
│   ├── __init__.py
│   ├── technical_service.py
│   ├── indicators.py
│   └── SKILL.md
├── ths-edb-skill/
│   └── SKILL.md
└── ths-skill/
    └── SKILL.md
```

---

**报告生成时间**: 2025-03-25  
**报告版本**: v1.0
