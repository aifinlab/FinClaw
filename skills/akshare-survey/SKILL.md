---
name: "akshare-survey"
description: "机构调研Skill - 提供调研记录、调研热度排行、调研问答分析 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-survey

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-survey |
| **版本** | 1.1.0 |
| **分类** | 机构调研 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

机构调研Skill，提供A股市场机构调研记录查询、调研热度排行、调研问答分析等功能。追踪机构关注的热点公司和行业。

## 触发意图

### 主要触发词
- "机构调研"、"调研"
- "调研记录"
- "调研热度"
- "被调研"
- "接待机构"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 最新机构调研 | survey_latest | survey_latest.py --limit 30 |
| 茅台调研记录 | survey_stock | survey_stock.py --code 600519 |
| 调研热度排行 | survey_rank | survey_rank.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 调研数据 | AkShare-交易所 | - | 无需 |

## 功能列表

### 1. 最新调研
- **功能描述**: 获取最新机构调研记录
- **输入参数**: 数量限制
- **输出格式**: Markdown表格
- **数据源**: AkShare-交易所
- **使用示例**:
  ```bash
  python scripts/survey_latest.py --limit 30
  ```

### 2. 个股调研
- **功能描述**: 查询特定股票的调研历史
- **输入参数**: 股票代码
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/survey_stock.py --code 600519
  ```

### 3. 调研热度排行
- **功能描述**: 调研次数排行
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/survey_rank.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| survey_latest.py | 最新调研 | ✅ |
| survey_stock.py | 个股调研 | ✅ |
| survey_rank.py | 调研排行 | ✅ |

## 调研信号解读

| 情形 | 信号 |
|:---|:---|
| 近期被多家机构密集调研 | 机构关注度高，可能有催化剂 |
| 知名机构（公募基金）调研 | 潜在配置意向 |
| 调研后股价异动 | 调研内容可能有重大信息 |
| 冷门股突然被调研 | 可能存在预期差 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare-交易所
⏱️ **数据时间**: 2026-03-19
📌 **调研日期**: 2026-03-15
📌 **接待机构**: xx基金、xx证券
🔗 **原始来源**: 上市公司投资者关系活动记录
🔧 **分析工具**: FinClaw v1.0
```

## 依赖要求

```
akshare>=1.10.0
pandas>=1.3.0
pyyaml>=5.4.0
```

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
