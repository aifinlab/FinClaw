---
name: "akshare-reits"
description: "REITs数据Skill - 提供公募REITs行情、收益分析、资产类型筛选 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-reits

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-reits |
| **版本** | 1.1.0 |
| **分类** | REITs数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

REITs（房地产投资信托基金）数据Skill，提供A股公募REITs基金列表、行情查询、收益分析、按资产类型筛选、分红统计等功能。

## 触发意图

### 主要触发词
- "REITs"、"公募REITs"
- "基础设施REITs"
- "产业园REITs"、"高速公路REITs"
- "REITs分红"、"REITs收益"
- "REITs行情"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| REITs列表 | reits_list | reits_list.py |
| REITs行情 | reits_quote | reits_quote.py |
| 产业园REITs | reits_type | reits_type.py --type 产业园 |
| REITs分红 | reits_dividend | reits_dividend.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| REITs数据 | AkShare | - | 无需 |

## REITs资产类型

| 类型 | 代表产品 | 收益特征 |
|:---|:---|:---|
| **产业园** | 东吴苏园REIT、博时蛇口REIT | 租金收益+增值 |
| **仓储物流** | 中金普洛斯REIT、红土盐田港REIT | 稳定租金 |
| **高速公路** | 平安广州广河REIT、浙商沪杭甬REIT | 过路费收入 |
| **生态环保** | 中航首钢绿能REIT、富国首创水务REIT | 特许经营权 |
| **保障房** | 华夏北京保障房REIT、中金厦门安居REIT | 租金收入 |
| **能源** | 鹏华深圳能源REIT、中信建投国家电投REIT | 发电收入 |

## 功能列表

### 1. REITs列表
- **功能描述**: 获取全市场公募REITs基金列表
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/reits_list.py
  ```

### 2. REITs行情
- **功能描述**: 获取REITs实时行情
- **输入参数**: REITs代码（可选）
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/reits_quote.py
  python scripts/reits_quote.py --code 180101
  ```

### 3. 按类型筛选
- **功能描述**: 按资产类型筛选REITs
- **输入参数**: 资产类型
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/reits_type.py --type 产业园
  python scripts/reits_type.py --type 高速公路
  ```

### 4. 分红统计
- **功能描述**: 获取REITs分红统计
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 分红公告后
- **使用示例**:
  ```bash
  python scripts/reits_dividend.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| reits_list.py | REITs列表 | ✅ |
| reits_quote.py | REITs行情 | ✅ |
| reits_type.py | 类型筛选 | ✅ |
| reits_dividend.py | 分红统计 | ✅ |

## REITs投资特点

| 特点 | 说明 |
|:---|:---|
| **强制分红** | 收益分配比例≥90% |
| **稳定现金流** | 底层资产产生稳定收益 |
| **低相关性** | 与股票/债券相关性低 |
| **流动性** | 交易所上市交易 |
| **透明度** | 定期披露运营数据 |

## 收益来源

| 来源 | 占比 | 特点 |
|:---|:---:|:---|
| **分红收益** | 70-80% | 稳定现金流入 |
| **资本增值** | 20-30% | 底层资产升值 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare
⏱️ **数据时间**: 2026-03-19
📌 **REITs代码**: 180101
📌 **资产类型**: 产业园
🔗 **交易所**: 深圳证券交易所
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
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增6大资产类型 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
