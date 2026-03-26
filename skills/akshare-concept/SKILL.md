---
name: "akshare-concept"
description: "概念板块Skill - 提供概念板块行情、龙头股、资金流向 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-concept

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-concept |
| **版本** | 1.1.0 |
| **分类** | 概念板块 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

概念板块Skill，提供A股市场概念板块行情、板块资金流向、龙头股分析、热点题材追踪等功能。覆盖人工智能、芯片、新能源等热门概念。

## 触发意图

### 主要触发词
- "概念"、"概念板块"
- "人工智能"、"AI"、"ChatGPT"
- "芯片"、"半导体"
- "新能源"、"锂电池"
- "龙头股"、"热点"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 概念板块列表 | concept_list | concept_list.py |
| 人工智能板块 | concept_quote | concept_quote.py --name 人工智能 |
| 芯片概念龙头 | concept_stocks | concept_stocks.py --name 芯片 |
| 热点题材 | concept_hot | concept_list.py --hot |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 概念板块 | AkShare-同花顺 | - | 无需 |
| 资金流向 | AkShare | - | 无需 |

## 热门概念板块

| 概念 | 代表个股 | 驱动因素 |
|:---|:---|:---|
| **人工智能** | 科大讯飞、寒武纪 | ChatGPT、大模型 |
| **芯片/半导体** | 中芯国际、北方华创 | 国产替代 |
| **新能源** | 宁德时代、比亚迪 | 碳中和、电动化 |
| **光伏** | 隆基绿能、通威股份 | 清洁能源 |
| **充电桩** | 特锐德、盛弘股份 | 新基建 |
| **数字经济** | 浪潮信息、中科曙光 | 政策驱动 |
| **中特估** | 中国移动、中国石油 | 估值修复 |
| **减肥药** | 常山药业、翰宇药业 | 海外映射 |

## 功能列表

### 1. 概念板块列表
- **功能描述**: 获取概念板块列表
- **输入参数**: 无（全部）或热门筛选
- **输出格式**: Markdown表格
- **数据源**: AkShare-同花顺
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/concept_list.py
  python scripts/concept_list.py --hot
  ```

### 2. 板块行情
- **功能描述**: 获取特定概念板块行情
- **输入参数**: 板块名称
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/concept_quote.py --name 人工智能
  python scripts/concept_quote.py --name 芯片
  ```

### 3. 板块个股
- **功能描述**: 获取概念板块成分股及龙头
- **输入参数**: 板块名称
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/concept_stocks.py --name 新能源
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| concept_list.py | 概念板块列表 | ✅ |
| concept_quote.py | 板块行情 | ✅ |
| concept_stocks.py | 板块个股 | ✅ |

## 概念投资注意

| 风险 | 说明 |
|:---|:---|
| **概念炒作** | 缺乏业绩支撑，波动大 |
| **热点轮动** | 热点切换快，追高风险 |
| **龙头股风险** | 涨幅过大后回调风险 |
| **政策依赖** | 部分概念依赖政策驱动 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: AkShare-同花顺
⏱️ **数据时间**: 2026-03-19
📌 **概念名称**: 人工智能
🔗 **原始来源**: 同花顺概念板块
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
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增热门概念 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
