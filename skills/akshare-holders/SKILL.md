---
name: "akshare-holders"
description: "股东数据Skill - 提供股东增减持、机构持仓、筹码分布、十大流通股东 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-holders

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-holders |
| **版本** | 1.1.0 |
| **分类** | 股东数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

股东数据Skill，提供股东增减持动态、机构持仓变化、筹码分布分析、十大流通股东等信息。追踪大股东、机构、散户的持仓变动，识别主力进出信号。

## 触发意图

### 主要触发词
- "股东"、"大股东"、"十大股东"
- "增减持"、"增持"、"减持"
- "机构持仓"、"基金持仓"
- "筹码分布"、"筹码集中度"
- "股东人数"、"散户数量"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 茅台股东增减持 | holders_change | holders_change.py 600519 |
| 机构持仓情况 | holders_institutional | holders_institutional.py 600519 |
| 筹码分布如何？ | holders_chips | holders_chips.py 600519 |
| 最新十大股东 | holders_top10 | holders_change.py --detail |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 股东增减持 | AkShare-交易所 | - | 无需 |
| 机构持仓 | AkShare-交易所 | - | 无需 |
| 筹码分布 | AkShare | - | 无需 |
| 十大股东 | AkShare-交易所 | - | 无需 |

## 功能列表

### 1. 股东增减持
- **功能描述**: 获取大股东增减持动态
- **输入参数**: 股票代码
- **输出格式**: Markdown表格（增减持人/变动数量/均价/变动后持股）
- **数据源**: AkShare-交易所
- **数据时效**: 日频（公告后更新）
- **使用示例**:
  ```bash
  python scripts/holders_change.py 600519
  python scripts/holders_change.py --detail  # 详细持股变动
  ```

### 2. 机构持仓
- **功能描述**: 获取基金、QFII等机构持仓数据
- **输入参数**: 股票代码
- **输出格式**: Markdown表格
- **数据源**: AkShare-交易所
- **数据时效**: 季度（财报披露后）
- **使用示例**:
  ```bash
  python scripts/holders_institutional.py 600519
  ```

### 3. 筹码分布
- **功能描述**: 分析筹码集中度、筹码成本区间
- **输入参数**: 股票代码
- **输出格式**: Markdown报告
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/holders_chips.py 600519
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| holders_change.py | 股东增减持 | ✅ |
| holders_institutional.py | 机构持仓 | ✅ |
| holders_chips.py | 筹码分布 | ✅ |

## 增减持解读

### 增持信号
| 情形 | 信号强度 | 解读 |
|:---|:---:|:---|
| 大股东增持 >5% | ⭐⭐⭐⭐⭐ | 强烈看好，底部信号 |
| 董监高增持 | ⭐⭐⭐⭐ | 管理层信心 |
| 机构大幅增持 | ⭐⭐⭐ | 机构调研后加仓 |
| 小股东增持 | ⭐⭐ | 一般性投资 |

### 减持信号
| 情形 | 信号强度 | 解读 |
|:---|:---:|:---|
| 大股东减持 >5% | 🔴🔴🔴🔴🔴 | 重大利空 |
| 董监高减持 | 🔴🔴🔴🔴 | 需警惕 |
| 机构大幅减持 | 🔴🔴🔴 | 机构看空 |
| 解禁后减持 | 🔴🔴 | 正常套现 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare-交易所
⏱️ **数据时间**: 2026-03-19
📌 **数据类型**: 股东增减持
🔗 **原始来源**: 上市公司公告
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
