---
name: "akshare-fof"
description: "FOF基金Skill - 提供FOF净值、业绩排行、持仓穿透、养老目标基金 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-fof

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-fof |
| **版本** | 1.1.0 |
| **分类** | FOF基金 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

FOF（基金中的基金）Skill，提供FOF基金净值查询、业绩排行、持仓穿透分析、养老目标基金专题等功能。

## 触发意图

### 主要触发词
- "FOF"、"基金中的基金"
- "养老目标基金"
- "FOF业绩"
- "FOF持仓"
- "养老FOF"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| FOF基金列表 | fof_list | fof_list.py |
| FOF净值 | fof_nav | fof_nav.py --code 006308 |
| FOF业绩排行 | fof_rank | fof_rank.py --period 1y |
| 养老目标基金 | fof_pension | fof_pension.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| FOF数据 | AkShare | - | 无需 |

## FOF特点

| 特点 | 说明 |
|:---|:---|
| **双重收费** | FOF管理费+底层基金费用 |
| **分散投资** | 投资多只基金，二次分散 |
| **专业选基** | 基金经理专业筛选基金 |
| **适合人群** | 没有时间研究基金的投资者 |

## 功能列表

### 1. FOF列表
- **功能描述**: 获取FOF基金列表
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/fof_list.py
  ```

### 2. FOF净值
- **功能描述**: 查询FOF基金净值
- **输入参数**: 基金代码
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/fof_nav.py --code 006308
  ```

### 3. FOF业绩排行
- **功能描述**: FOF业绩排行
- **输入参数**: 时间周期
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/fof_rank.py --period 1y
  ```

### 4. 养老目标基金
- **功能描述**: 获取养老目标FOF
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/fof_pension.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| fof_list.py | FOF列表 | ✅ |
| fof_nav.py | FOF净值 | ✅ |
| fof_rank.py | FOF排行 | ✅ |
| fof_pension.py | 养老FOF | ✅ |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare
⏱️ **数据时间**: 2026-03-19
📌 **基金类型**: FOF
🔗 **原始来源**: 基金业协会
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
