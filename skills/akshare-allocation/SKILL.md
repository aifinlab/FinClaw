---
name: "akshare-allocation"
description: "资产配置Skill - 提供基金资产配置、行业分布、重仓股分析 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-allocation

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-allocation |
| **版本** | 1.1.0 |
| **分类** | 资产配置 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

资产配置Skill，提供公募基金资产配置结构（股票/债券/现金）、行业分布、重仓股分析、持仓变动追踪等功能。分析基金投资组合特征。

## 触发意图

### 主要触发词
- "资产配置"、"基金配置"
- "重仓股"、"持仓"
- "行业分布"、"行业配置"
- "股票仓位"、"债券仓位"
- "持仓变动"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 基金资产配置 | allocation_asset | allocation_asset.py --code 006308 |
| 行业分布 | allocation_sector | allocation_sector.py --code 006308 |
| 重仓股分析 | allocation_holdings | allocation_holdings.py --code 006308 |
| 持仓变动 | allocation_change | allocation_change.py --code 006308 |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 基金持仓 | AkShare | - | 无需 |

## 功能列表

### 1. 资产配置
- **功能描述**: 获取基金资产配置（股票/债券/现金比例）
- **输入参数**: 基金代码
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 季报/年报
- **使用示例**:
  ```bash
  python scripts/allocation_asset.py --code 006308
  ```

### 2. 行业配置
- **功能描述**: 获取基金行业分布
- **输入参数**: 基金代码
- **输出格式**: Markdown表格 + 饼图描述
- **数据源**: AkShare
- **数据时效**: 季报/年报
- **使用示例**:
  ```bash
  python scripts/allocation_sector.py --code 006308
  ```

### 3. 重仓股分析
- **功能描述**: 获取基金前十大重仓股
- **输入参数**: 基金代码
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 季报/年报
- **使用示例**:
  ```bash
  python scripts/allocation_holdings.py --code 006308
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| allocation_asset.py | 资产配置 | ✅ |
| allocation_sector.py | 行业配置 | ✅ |
| allocation_holdings.py | 重仓股分析 | ✅ |

## 资产配置类型

| 类型 | 股票仓位 | 适合市场 |
|:---|:---:|:---|
| **偏股型** | >60% | 牛市 |
| **平衡型** | 40-60% | 震荡市 |
| **偏债型** | <40% | 熊市 |
| **债券型** | 0-20% | 保守 |
| **货币型** | 0% | 现金管理 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare
⏱️ **数据时间**: 2026-03-19
📌 **报告期**: 2025Q4
📌 **基金代码**: 006308
🔗 **原始来源**: 基金季报
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
