---
name: "zhitu-data"
description: "智兔数服数据Skill - 免注册A股/港股/基金实时行情、历史K线、技术指标 via 智兔数服"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["requests", "pandas", "pyyaml"]
---

# SKILL.md - zhitu-data

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | zhitu-data |
| **版本** | 1.1.0 |
| **分类** | 免费数据源 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

智兔数服数据Skill，提供免注册、免费的A股、港股、基金实时行情、历史K线数据、技术指标（MACD/KDJ/BOLL/MA）。作为备用数据源使用。

## 触发意图

### 主要触发词
- "智兔"、"zhitu"
- "免费行情"
- "免注册数据"
- "备用数据源"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 查茅台行情（智兔） | zhitu_quote | zhitu_quote.py 600519 |
| 历史K线 | zhitu_hist | zhitu_hist.py 600519 20240101 20260319 |
| MACD指标 | zhitu_tech | zhitu_tech.py 600519 MACD |
| 股票列表 | zhitu_list | zhitu_list.py |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 实时行情 | 智兔数服 | - | 免注册（测试Token） |
| 历史K线 | 智兔数服 | - | 免注册 |
| 技术指标 | 智兔数服 | - | 免注册 |

## 支持的市场

| 市场 | 代码格式 | 示例 |
|:---|:---|:---|
| 上海A股 | 600000.SH 或 600000 | 600519 |
| 深圳A股 | 000001.SZ 或 000001 | 000001 |
| 创业板 | 300001.SZ 或 300001 | 300750 |
| 科创板 | 688001.SH 或 688001 | 688981 |
| 北交所 | 430047.BJ 或 430047 | 430047 |
| 港股 | 00001.HK 或 00001 | 00700 |
| 基金 | 510300.SH 或 510300 | 510300 |

## 功能列表

### 1. 实时行情
- **功能描述**: 获取实时行情数据
- **输入参数**: 股票代码
- **输出格式**: Markdown表格
- **数据源**: 智兔数服
- **使用示例**:
  ```bash
  python scripts/zhitu_quote.py 600519
  python scripts/zhitu_quote.py 600519.SH
  ```

### 2. 历史K线
- **功能描述**: 获取历史K线数据
- **输入参数**: 股票代码、开始日期、结束日期
- **输出格式**: CSV/Markdown
- **数据源**: 智兔数服
- **使用示例**:
  ```bash
  python scripts/zhitu_hist.py 600519 20240101 20260319
  ```

### 3. 技术指标
- **功能描述**: 计算技术指标（MACD/KDJ/BOLL/MA）
- **输入参数**: 股票代码、指标类型
- **输出格式**: Markdown表格
- **数据源**: 智兔数服
- **使用示例**:
  ```bash
  python scripts/zhitu_tech.py 600519 MACD
  python scripts/zhitu_tech.py 600519 KDJ
  python scripts/zhitu_tech.py 600519 BOLL
  python scripts/zhitu_tech.py 600519 MA
  ```

### 4. 股票列表
- **功能描述**: 获取股票列表
- **输入参数**: 市场（可选）
- **输出格式**: Markdown表格
- **数据源**: 智兔数服
- **使用示例**:
  ```bash
  python scripts/zhitu_list.py
  python scripts/zhitu_list.py sh
  ```

## 技术指标说明

| 指标 | 说明 | 用法 |
|:---|:---|:---|
| **MACD** | 指数平滑异同平均线 | DIF上穿DEA买入 |
| **KDJ** | 随机指标 | K上穿D买入，超买超卖 |
| **BOLL** | 布林带 | 价格触及下轨买入 |
| **MA** | 移动平均线 | 价格站上均线买入 |

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| zhitu_quote.py | 实时行情 | ✅ |
| zhitu_hist.py | 历史K线 | ✅ |
| zhitu_tech.py | 技术指标 | ✅ |
| zhitu_list.py | 股票列表 | ✅ |

## 特点对比

| 特性 | 智兔数服 | 其他API |
|:---|:---|:---|
| **注册** | 免注册 | 通常需要 |
| **费用** | 免费 | 免费/付费 |
| **A股覆盖** | 全覆盖 | 部分 |
| **港股** | 支持 | 视API而定 |
| **北交所** | 支持 | 较少 |
| **技术指标** | 内置 | 视API而定 |
| **调用限制** | 较宽松 | 较严格 |

## 数据来源标注规范

```markdown
---
📊 **数据来源**: 智兔数服
⏱️ **数据时间**: 2026-03-19 10:30:15
🔗 **原始来源**: 智兔数服API
🔧 **分析工具**: FinClaw v1.0
```

## 依赖要求

```
requests>=2.25.0
pandas>=1.3.0
pyyaml>=5.4.0
```

## 注意事项

- 测试Token可能有调用频率限制
- 生产环境建议申请正式API Key
- 数据仅供个人学习研究使用
- 港股数据可能有延迟

## 相关链接

- 智兔数服: https://zhituapi.com
- API文档: https://zhituapi.com/docs
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0 |
| 1.0.0 | 2026-03-13 | 初始版本 |

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
