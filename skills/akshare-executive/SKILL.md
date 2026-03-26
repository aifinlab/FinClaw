---
name: "akshare-executive"
description: "高管持股Skill - 提供高管增减持、持股变动、薪酬分析 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-executive

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-executive |
| **版本** | 1.1.0 |
| **分类** | 高管持股 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

高管持股Skill，提供A股上市公司高管（董事、监事、高管）的持股变动、增减持记录、薪酬分析等功能。追踪管理层信心信号。

## 触发意图

### 主要触发词
- "高管"、"董监高"
- "高管增持"、"高管减持"
- "管理层持股"
- "董事长"、"总经理"
- "内部人交易"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 高管增减持 | executive_change | executive_change.py --limit 30 |
| 茅台高管持股 | executive_stock | executive_stock.py --code 600519 |
| 高管增持排行 | executive_buy | executive_buy.py |
| 高管减持排行 | executive_sell | executive_sell.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 高管持股 | AkShare-交易所 | - | 无需 |

## 高管范围

| 职位 | 说明 |
|:---|:---|
| **董事** | 董事长、副董事长、独立董事 |
| **监事** | 监事会主席、监事 |
| **高管** | 总经理、副总经理、财务总监、董秘 |

## 功能列表

### 1. 高管增减持
- **功能描述**: 获取高管增减持动态
- **输入参数**: 数量限制
- **输出格式**: Markdown表格
- **数据源**: AkShare-交易所
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/executive_change.py --limit 30
  ```

### 2. 个股高管变动
- **功能描述**: 查询特定股票的高管持股变动
- **输入参数**: 股票代码
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/executive_stock.py --code 600519
  ```

### 3. 高管增持排行
- **功能描述**: 高管增持金额排行
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/executive_buy.py
  ```

### 4. 高管减持排行
- **功能描述**: 高管减持金额排行
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/executive_sell.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| executive_change.py | 高管增减持 | ✅ |
| executive_stock.py | 个股高管变动 | ✅ |
| executive_buy.py | 高管增持排行 | ✅ |
| executive_sell.py | 高管减持排行 | ✅ |

## 高管增减持信号

| 情形 | 信号强度 | 解读 |
|:---|:---:|:---|
| 董事长增持 | ⭐⭐⭐⭐⭐ | 最强烈信心信号 |
| 总经理增持 | ⭐⭐⭐⭐ | 管理层看好 |
| 多位高管同时增持 | ⭐⭐⭐⭐⭐ | 集体看好 |
| 小额增持（<50万） | ⭐⭐ | 象征性增持 |
| 高管减持（非解禁） | 🔴🔴🔴 | 需警惕 |
| 解禁后减持 | 🔴🔴 | 正常套现 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare-交易所
⏱️ **数据时间**: 2026-03-19
📌 **数据类型**: 高管增减持
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
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增高管增减持信号 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
