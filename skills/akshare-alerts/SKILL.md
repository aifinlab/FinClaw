---
name: "akshare-alerts"
description: "智能预警Skill - 提供价格预警、成交量预警、公告预警、技术指标预警 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-alerts

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-alerts |
| **版本** | 1.1.0 |
| **分类** | 智能预警 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

智能预警Skill，提供A股市场价格预警、成交量预警、涨跌停预警、公告预警、技术指标预警（金叉/死叉）等功能。帮助投资者及时捕捉市场异动。

## 触发意图

### 主要触发词
- "预警"、"提醒"
- "价格预警"、"突破"
- "成交量异常"
- "涨停"、"跌停"
- "金叉"、"死叉"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 设置价格预警 | alert_price | alert_price.py --code 000001 --above 15 |
| 跌幅预警 | alert_price | alert_price.py --code 000001 --below 12 |
| 涨跌停预警 | alert_limit | alert_limit.py |
| 成交量异常 | alert_volume | alert_volume.py --threshold 5 |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 预警数据 | AkShare | - | 无需 |

## 预警类型

| 类型 | 触发条件 | 用途 |
|:---|:---|:---|
| **价格突破** | 股价突破设定价位 | 捕捉突破机会 |
| **价格跌破** | 股价跌破设定价位 | 止损提醒 |
| **涨跌停** | 股票涨停或跌停 | 异动监控 |
| **成交量异常** | 成交量放大N倍 | 资金异动 |
| **公告预警** | 特定类型公告发布 | 事件驱动 |
| **技术指标** | 金叉/死叉等信号 | 技术交易 |

## 功能列表

### 1. 价格预警
- **功能描述**: 设置价格突破或跌破预警
- **输入参数**: 股票代码、价格、方向（above/below）
- **输出格式**: 预警通知
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/alert_price.py --code 000001 --above 15.0
  python scripts/alert_price.py --code 000001 --below 12.0
  ```

### 2. 涨跌停预警
- **功能描述**: 监控涨跌停股票
- **输入参数**: 无
- **输出格式**: Markdown列表
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/alert_limit.py
  ```

### 3. 成交量预警
- **功能描述**: 监控成交量异常放大
- **输入参数**: 倍数阈值
- **输出格式**: Markdown列表
- **数据源**: AkShare
- **使用示例**:
  ```bash
  python scripts/alert_volume.py --threshold 5
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| alert_price.py | 价格预警 | ✅ |
| alert_limit.py | 涨跌停预警 | ✅ |
| alert_volume.py | 成交量预警 | ✅ |

## 预警使用建议

| 场景 | 推荐预警 |
|:---|:---|
| 突破买入 | 价格突破 + 成交量放大 |
| 止损保护 | 价格跌破 + 技术指标死叉 |
| 事件驱动 | 公告预警 + 涨跌停监控 |
| 趋势跟踪 | 技术指标金叉/死叉 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare
⏱️ **预警时间**: 2026-03-19 10:30:15
📌 **预警类型**: 价格突破
🔗 **分析工具**: FinClaw v1.0
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
