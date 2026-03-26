---
name: "akshare-manager"
description: "基金经理Skill - 提供基金经理业绩排行、任期统计、在管基金查询 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-manager

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-manager |
| **版本** | 1.1.0 |
| **分类** | 基金经理 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

基金经理Skill，提供基金经理业绩排行、任期统计、在管基金查询、换手率分析等功能。追踪明星基金经理动向。

## 触发意图

### 主要触发词
- "基金经理"、"明星基金经理"
- "张坤"、"刘彦春"、"葛兰"
- "基金经理排行"
- "在管基金"
- "基金经理业绩"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 基金经理排行 | manager_rank | manager_rank.py --period 1y |
| 张坤管理的基金 | manager_funds | manager_funds.py --name 张坤 |
| 基金经理详情 | manager_detail | manager_detail.py --name 刘彦春 |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 基金经理 | AkShare | - | 无需 |

## 明星基金经理

| 基金经理 | 代表基金 | 投资风格 |
|:---|:---|:---|
| **张坤** | 易方达蓝筹精选 | 价值投资、重仓消费 |
| **刘彦春** | 景顺长城新兴成长 | 消费成长 |
| **葛兰** | 中欧医疗健康 | 医药专业 |
| **朱少醒** | 富国天惠成长 | 长期持有 |
| **谢治宇** | 兴全合润 | 均衡配置 |
| **傅鹏博** | 睿远成长价值 | 成长价值 |

## 功能列表

### 1. 基金经理排行
- **功能描述**: 基金经理业绩排行
- **输入参数**: 时间周期
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/manager_rank.py --period 1y
  ```

### 2. 基金经理详情
- **功能描述**: 查询基金经理详细信息
- **输入参数**: 经理姓名
- **输出格式**: Markdown报告
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/manager_detail.py --name 张坤
  ```

### 3. 在管基金
- **功能描述**: 查询基金经理管理的所有基金
- **输入参数**: 经理姓名
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/manager_funds.py --name 刘彦春
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| manager_rank.py | 经理排行 | ✅ |
| manager_detail.py | 经理详情 | ✅ |
| manager_funds.py | 在管基金 | ✅ |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare
⏱️ **数据时间**: 2026-03-19
📌 **基金经理**: 张坤
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
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增明星经理 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
