---
name: "akshare-macro"
description: "宏观经济数据Skill - 覆盖GDP、CPI、PPI、M2、PMI、LPR利率、人民币汇率等核心宏观指标 via AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-macro

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-macro |
| **版本** | 1.1.0 |
| **分类** | 宏观数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

宏观经济数据Skill，提供中国及全球主要经济体的核心宏观指标，包括GDP、CPI、PPI、M2、PMI、利率、汇率等。支持经济周期判断和宏观概览仪表盘。

## 触发意图

### 主要触发词
- "GDP"、"CPI"、"PPI"、"M2"、"PMI"
- "通胀"、"物价"、"货币供应量"
- "利率"、"LPR"、"汇率"、"人民币"
- "宏观经济"、"经济数据"、"经济周期"
- "国家统计局"、"央行数据"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 最新的GDP数据是多少？ | macro_gdp | macro_gdp.py |
| CPI涨了多少？ | macro_cpi | macro_cpi.py |
| 查询M2货币供应量 | macro_m2 | macro_m2.py |
| 制造业PMI怎么样？ | macro_pmi | macro_pmi.py |
| LPR利率下调了吗？ | macro_rate | macro_rate.py |
| 看一下宏观概览 | macro_summary | macro_summary.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| GDP/CPI/PPI | AkShare-国家统计局 | - | 无需 |
| M2货币供应量 | AkShare-中国人民银行 | - | 无需 |
| PMI | AkShare-国家统计局 | - | 无需 |
| LPR利率 | AkShare-央行 | - | 无需 |
| 人民币汇率 | AkShare-央行/外汇局 | - | 无需 |

## 功能列表

### 1. GDP数据
- **功能描述**: 获取GDP季度/年度数据及同比增速
- **输入参数**: 无（自动获取最新）
- **输出格式**: Markdown表格（季度、GDP值、同比、环比）
- **数据源**: AkShare-国家统计局
- **数据时效**: 季度更新，发布后次日可用
- **使用示例**:
  ```bash
  python scripts/macro_gdp.py
  ```

### 2. CPI通胀数据
- **功能描述**: 获取CPI同比、环比及核心CPI数据
- **输入参数**: 无
- **输出格式**: Markdown表格（月份、CPI同比、环比、核心CPI）
- **数据源**: AkShare-国家统计局
- **数据时效**: 月度更新，每月9-10日发布上月数据
- **使用示例**:
  ```bash
  python scripts/macro_cpi.py
  ```

### 3. PPI生产者物价
- **功能描述**: 获取PPI同比、环比数据
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare-国家统计局
- **数据时效**: 月度更新
- **使用示例**:
  ```bash
  python scripts/macro_ppi.py
  ```

### 4. M2货币供应量
- **功能描述**: 获取M2、M1余额及同比增速
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare-中国人民银行
- **数据时效**: 月度更新，每月10-15日发布上月数据
- **使用示例**:
  ```bash
  python scripts/macro_m2.py
  ```

### 5. 制造业PMI
- **功能描述**: 获取官方制造业PMI及分项指数
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare-国家统计局
- **数据时效**: 月度更新，每月月底发布当月数据
- **使用示例**:
  ```bash
  python scripts/macro_pmi.py
  ```

### 6. LPR利率与汇率
- **功能描述**: 获取贷款市场报价利率(LPR)及人民币汇率
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: AkShare-央行/外汇局
- **数据时效**: LPR每月20日更新（遇节假日顺延），汇率日频
- **使用示例**:
  ```bash
  python scripts/macro_rate.py
  ```

### 7. 宏观概览仪表盘
- **功能描述**: 综合展示GDP、CPI、PMI等核心指标，自动判断经济周期
- **输入参数**: 无
- **输出格式**: Markdown报告（含经济周期判断）
- **数据源**: 多源聚合
- **数据时效**: 综合各数据源
- **使用示例**:
  ```bash
  python scripts/macro_summary.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| macro_gdp.py | GDP季度/年度数据 | ✅ |
| macro_cpi.py | CPI通胀数据 | ✅ |
| macro_ppi.py | PPI生产者物价 | ✅ |
| macro_m2.py | M2货币供应量 | ✅ |
| macro_pmi.py | 制造业PMI | ✅ |
| macro_rate.py | LPR利率/人民币汇率 | ✅ |
| macro_summary.py | 宏观概览仪表盘 | ✅ |

## 数据字段说明

### GDP数据字段
| 字段 | 说明 |
|:---|:---|
| `quarter` | 季度（如2026Q1） |
| `gdp` | GDP累计值（亿元） |
| `gdp_yoy` | GDP同比增长（%） |
| `gdp_qoq` | GDP环比增长（%） |

### CPI数据字段
| 字段 | 说明 |
|:---|:---|
| `date` | 日期 |
| `cpi` | CPI同比（%） |
| `cpi_mom` | CPI环比（%） |
| `core_cpi` | 核心CPI（%） |

### M2数据字段
| 字段 | 说明 |
|:---|:---|
| `date` | 日期 |
| `m2` | M2余额（万亿元） |
| `m2_yoy` | M2同比增长（%） |
| `m1_yoy` | M1同比增长（%） |
| `m0_yoy` | M0同比增长（%） |

## 经济周期判断

基于GDP+CPI+PMI综合判断经济周期阶段：

| 周期阶段 | GDP | CPI | PMI | 特征 |
|:---|:---:|:---:|:---:|:---|
| **复苏期** | ↑ | ↓ | >50 | 经济触底回升，通胀低位 |
| **过热期** | ↑ | ↑ | >50 | 经济高增长，通胀上行 |
| **滞胀期** | ↓ | ↑ | <50 | 经济放缓，通胀高企 |
| **衰退期** | ↓ | ↓ | <50 | 经济收缩，通缩风险 |

## 使用示例

### 命令行调用
```bash
# GDP数据
python scripts/macro_gdp.py

# CPI通胀
python scripts/macro_cpi.py

# M2货币供应
python scripts/macro_m2.py

# 制造业PMI
python scripts/macro_pmi.py

# LPR利率
python scripts/macro_rate.py

# 宏观概览
python scripts/macro_summary.py
```

## 数据来源标注规范

本Skill所有输出数据将按以下格式标注来源：

```markdown
---
📊 **数据来源**: AkShare-国家统计局/中国人民银行
⏱️ **数据时间**: 2026-03-19 10:30:15
📌 **报告期**: 2026年2月
🔗 **原始来源**: http://www.stats.gov.cn / http://www.pbc.gov.cn
🔧 **分析工具**: FinClaw v1.0
```

## 依赖要求

```
akshare>=1.10.0
pandas>=1.3.0
pyyaml>=5.4.0
```

## 数据发布日历

| 指标 | 发布频率 | 发布时间 |
|:---|:---:|:---|
| GDP | 季度 | 季后15-20日 |
| CPI/PPI | 月度 | 每月9-10日 |
| M2/M1 | 月度 | 每月10-15日 |
| PMI | 月度 | 每月月底 |
| LPR | 月度 | 每月20日 |

## 性能指标

| 指标 | 目标值 | 当前值 |
|:---|:---:|:---:|
| 数据更新延迟 | < 48小时 | ~24小时 |
| 可用性 | > 95% | 98% |
| 数据准确率 | > 98% | 99% |

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增数据来源强制标注、经济周期判断 |
| 1.0.0 | 2026-03-13 | 初始版本 |

## 相关链接

- AkShare文档: https://www.akshare.xyz
- 国家统计局: http://www.stats.gov.cn
- 中国人民银行: http://www.pbc.gov.cn
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
