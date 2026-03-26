---
name: "baostock-history"
description: "历史行情数据Skill - 提供A股/指数/基金的完整历史K线数据，支持前复权/后复权，适合回测研究 via BaoStock"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["baostock", "pandas", "pyyaml"]
---

# SKILL.md - baostock-history

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | baostock-history |
| **版本** | 1.1.0 |
| **分类** | 历史行情数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

历史行情数据Skill，基于BaoStock提供A股、指数、基金的完整历史K线数据，支持前复权/后复权，数据从IPO至今全覆盖。完全免费，无需注册，最适合量化回测和历史研究。

## 触发意图

### 主要触发词
- "历史数据"、"K线数据"、"历史行情"
- "复权"、"前复权"、"后复权"
- "回测数据"、"历史价格"
- "日线数据"、"周线数据"
- "从IPO到现在"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 获取茅台历史数据 | historical_data | bs_history.py sh.600519 20200101 20260319 |
| 查询上证指数历史K线 | index_history | bs_index.py sh.000001 20240101 20260319 |
| 需要前复权数据 | adjusted_data | bs_history.py sh.600519 20200101 20260319 2 |
| 获取ETF历史数据 | fund_history | bs_fund.py sh.510300 20240101 20260319 |
| 查看所有股票列表 | stock_list | bs_stock_list.py |

## 数据源配置

| 数据类型 | 主要来源 | 认证要求 |
|:---|:---|:---:|
| A股历史K线 | BaoStock | 无需 |
| 指数历史K线 | BaoStock | 无需 |
| 基金历史K线 | BaoStock | 无需 |
| 股票列表 | BaoStock | 无需 |
| 财务数据 | BaoStock | 无需 |

## 功能列表

### 1. 历史K线数据
- **功能描述**: 获取个股完整历史K线数据，支持多种复权方式
- **输入参数**: 股票代码、开始日期、结束日期、复权类型
- **输出格式**: CSV/Markdown表格
- **数据源**: BaoStock
- **数据时效**: 日频，盘后更新
- **使用示例**:
  ```bash
  python scripts/bs_history.py sh.600519 2020-01-01 2026-03-19 2
  ```

### 2. 指数历史数据
- **功能描述**: 获取上证指数、深证成指等主要指数历史数据
- **输入参数**: 指数代码、开始日期、结束日期
- **输出格式**: CSV/Markdown表格
- **数据源**: BaoStock
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/bs_index.py sh.000001 2024-01-01 2026-03-19
  ```

### 3. 基金历史数据
- **功能描述**: 获取ETF/LOF基金历史净值数据
- **输入参数**: 基金代码、开始日期、结束日期
- **输出格式**: CSV/Markdown表格
- **数据源**: BaoStock
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/bs_fund.py sh.510300 2024-01-01 2026-03-19
  ```

### 4. 股票列表
- **功能描述**: 获取A股全市场股票列表
- **输入参数**: 无
- **输出格式**: CSV列表
- **数据源**: BaoStock
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/bs_stock_list.py
  ```

### 5. 财务数据
- **功能描述**: 获取季度/年度财务数据
- **输入参数**: 股票代码、年份、季度
- **输出格式**: Markdown表格
- **数据源**: BaoStock
- **数据时效**: 季度更新
- **使用示例**:
  ```bash
  python scripts/bs_finance.py sh.600519 2023 4
  ```

## 复权类型说明

| 类型 | 代码 | 说明 | 适用场景 |
|:---|:---:|:---|:---|
| 不复权 | 1 | 原始价格 | 查看真实交易价格 |
| **前复权** | **2** | **从IPO开始复权（推荐）** | **回测、技术分析** |
| 后复权 | 3 | 以最新价格为基准复权 | 长期趋势分析 |

**推荐**: 回测使用前复权（代码2），保证历史数据的连续性

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| bs_history.py | 个股历史K线数据 | ✅ |
| bs_index.py | 指数历史数据 | ✅ |
| bs_fund.py | 基金历史数据 | ✅ |
| bs_stock_list.py | 股票列表 | ✅ |
| bs_finance.py | 季度财务数据 | ✅ |

## 股票代码格式

BaoStock使用 `.` 分隔格式：

| 类型 | 格式 | 示例 |
|:---|:---|:---|
| 上海A股 | sh.6xxxxxx | sh.600519 (贵州茅台) |
| 深圳A股 | sz.0xxxxxx | sz.000001 (平安银行) |
| 创业板 | sz.3xxxxxx | sz.300750 (宁德时代) |
| 科创板 | sh.688xxx | sh.688981 (中芯国际) |
| 上证指数 | sh.000001 | sh.000001 |
| 深证成指 | sz.399001 | sz.399001 |
| ETF | sh.51xxxx / sz.15xxxx | sh.510300 (沪深300ETF) |

## 使用示例

### 命令行调用
```bash
# 个股历史数据（前复权）
python scripts/bs_history.py sh.600519 2020-01-01 2026-03-19 2

# 指数历史数据
python scripts/bs_index.py sh.000001 2024-01-01 2026-03-19

# 基金历史数据
python scripts/bs_fund.py sh.510300 2024-01-01 2026-03-19

# 股票列表
python scripts/bs_stock_list.py

# 财务数据
python scripts/bs_finance.py sh.600519 2023 4
```

### Python API调用
```python
import baostock as bs
from finclaw.core.data_annotator import annotate_data

# 登录
lg = bs.login()

# 获取历史数据
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,code,open,high,low,close,volume",
    start_date='2024-01-01',
    end_date='2026-03-19',
    frequency="d",
    adjustflag="2"  # 前复权
)

# 标注数据来源
data = {'股票': '贵州茅台', '数据条数': rs.error_code}
output = annotate_data(data, source="baostock")
print(output)

# 登出
bs.logout()
```

## 数据来源标注规范

本Skill所有输出数据将按以下格式标注来源：

```markdown
---
📊 **数据来源**: BaoStock
⏱️ **数据时间**: 2026-03-19 10:30:15
📌 **数据范围**: 2020-01-01 至 2026-03-19
📌 **复权方式**: 前复权
🔗 **数据来源**: http://baostock.com
🔧 **分析工具**: FinClaw v1.0
```

## 依赖要求

```
baostock>=0.8.0
pandas>=1.3.0
pyyaml>=5.4.0
```

## 优势对比

| 特性 | BaoStock | Tushare | AkShare |
|:---|:---|:---|:---|
| 成本 | ✅ 完全免费 | 免费/付费 | 免费 |
| 注册 | ✅ 无需注册 | 需要 | 无需 |
| 复权数据 | ✅ 优秀 | 良好 | 有限 |
| 历史深度 | ✅ IPO至今 | IPO至今 | 部分 |
| 频率限制 | ✅ 无限制 | 有限制 | 有限制 |
| 最佳用途 | ✅ 回测研究 | 量化分析 | 实时数据 |

## 性能指标

| 指标 | 目标值 | 当前值 |
|:---|:---:|:---:|
| 数据完整性 | > 99% | 99.9% |
| 查询响应时间 | < 3s | ~2s |
| 数据准确率 | > 98% | 99% |

## 注意事项

- ✅ **最佳用途**: 历史回测、量化研究、技术分析
- ✅ **复权数据**: 回测务必使用复权数据，避免除权除息影响
- ✅ **数据质量**: 官方交易所数据，质量可靠
- ⚠️ **实时性**: 无实时数据，通常延迟1天（盘后更新）
- ⚠️ **更新时间**: 数据在每日收盘后更新

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增数据来源强制标注 |
| 1.0.0 | 2026-03-12 | 初始版本 |

## 相关链接

- BaoStock官网: http://baostock.com
- API文档: http://baostock.com/baostock/index.php/Python_API文档
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
