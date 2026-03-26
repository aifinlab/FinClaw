---
name: "akshare-qfii"
description: "QFII/QDII数据Skill - 提供QFII持仓、QDII基金、外资动向分析 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-qfii

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-qfii |
| **版本** | 1.1.0 |
| **分类** | QFII/QDII |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

QFII/QDII数据Skill，提供QFII（合格境外机构投资者）持仓、QDII（合格境内机构投资者）基金、外资动向分析等功能。

## 触发意图

### 主要触发词
- "QFII"、"外资"
- "QDII"、"海外基金"
- "外资持仓"
- "QFII重仓"
- "海外投资"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| QFII持仓 | qfii_holdings | qfii_holdings.py --year 2024 --quarter 3 |
| QDII基金列表 | qdii_list | qdii_list.py |
| QDII净值 | qdii_nav | qdii_nav.py --code 000041 |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| QFII/QDII | AkShare | - | 无需 |

## QFII vs QDII

| 维度 | QFII | QDII |
|:---|:---|:---|
| **方向** | 外资投资A股 | 内资投资海外 |
| **主体** | 境外机构 | 境内机构 |
| **标的** | A股/债券 | 海外股票/基金 |
| **额度** | 有额度限制 | 有额度限制 |

## 功能列表

### 1. QFII持仓
- **功能描述**: 查询QFII持仓数据
- **输入参数**: 年份、季度
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/qfii_holdings.py --year 2024 --quarter 3
  ```

### 2. QDII基金列表
- **功能描述**: 获取QDII基金列表
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/qdii_list.py
  ```

### 3. QDII净值
- **功能描述**: 查询QDII基金净值
- **输入参数**: 基金代码
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/qdii_nav.py --code 000041
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| qfii_holdings.py | QFII持仓 | ✅ |
| qdii_list.py | QDII列表 | ✅ |
| qdii_nav.py | QDII净值 | ✅ |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare
⏱️ **数据时间**: 2026-03-19
📌 **数据类型**: QFII持仓/QDII基金
🔗 **原始来源**: 证监会/基金业协会
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
