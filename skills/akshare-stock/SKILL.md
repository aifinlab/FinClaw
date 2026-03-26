---
name: "akshare-stock"
description: "A股股票数据Skill - 提供实时行情、历史数据、板块分析、资金流向等 via AkShare/腾讯财经"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "requests", "pyyaml"]
---

# SKILL.md - akshare-stock

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-stock |
| **版本** | 1.1.0 |
| **分类** | 股票数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

A股股票数据Skill，提供实时行情、历史数据、板块分析、资金流向、龙虎榜等全方位A股数据服务。优先使用腾讯财经API（稳定、快速），备用AkShare（东方财富数据源）。

## 触发意图

### 主要触发词
- "股票"、"股价"、"行情"、"多少钱"、"涨了"、"跌了"
- "走势"、"K线"、"分时"、"实时"
- "600519"、"茅台"、"宁德时代"
- "查一下" + 股票名称/代码

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 茅台今天多少钱？ | stock_realtime | stock_quote_tx.py 600519 |
| 查一下宁德时代股价 | stock_realtime | stock_quote_tx.py 300750 |
| 半导体板块有哪些股票 | sector_analysis | stock_sector.py 半导体 |
| 今天资金流向如何 | capital_flow | stock_capital.py |
| 查询贵州茅台历史数据 | stock_history | stock_hist.py 600519 |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 实时行情 | 腾讯财经 | 新浪财经 | 无需 |
| 历史K线 | AkShare-东方财富 | Baostock | 无需 |
| 板块数据 | AkShare-东方财富 | - | 无需 |
| 资金流向 | AkShare-东方财富 | - | 无需 |
| 龙虎榜 | AkShare-东方财富 | - | 无需 |

## 功能列表

### 1. 实时行情查询
- **功能描述**: 获取A股实时行情数据
- **输入参数**: 股票代码（如 600519, 000001）
- **输出格式**: Markdown表格（价格、涨跌、成交量等）
- **数据源**: 腾讯财经 API
- **数据时效**: 实时（延迟<1秒）
- **使用示例**:
  ```bash
  python scripts/stock_quote_tx.py 600519
  ```

### 2. 股票搜索
- **功能描述**: 根据名称/拼音搜索股票代码
- **输入参数**: 股票名称关键词（如"茅台"、"银行"）
- **输出格式**: 匹配股票列表
- **数据源**: 腾讯财经 API
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/stock_search_tx.py 茅台
  ```

### 3. 板块分析
- **功能描述**: 查询特定板块/行业的成分股
- **输入参数**: 板块名称（如"半导体"、"银行"、"新能源"）
- **输出格式**: 板块成分股列表
- **数据源**: AkShare-东方财富
- **数据时效**: T日盘后更新
- **使用示例**:
  ```bash
  python scripts/stock_sector.py 半导体
  ```

### 4. 资金流向
- **功能描述**: 查询个股或市场资金流向
- **输入参数**: 市场(sh/sz/all)、数量限制
- **输出格式**: 资金流入/流出排行
- **数据源**: AkShare-东方财富
- **数据时效**: 实时（盘中更新）
- **使用示例**:
  ```bash
  python scripts/stock_capital.py --market sh --limit 30
  ```

### 5. 龙虎榜数据
- **功能描述**: 查询每日龙虎榜（营业部买卖情况）
- **输入参数**: 日期（YYYYMMDD格式，默认今日）
- **输出格式**: 龙虎榜详情表
- **数据源**: AkShare-东方财富
- **数据时效**: T日盘后
- **使用示例**:
  ```bash
  python scripts/stock_lhb.py
  python scripts/stock_lhb.py 20250311
  ```

### 6. 历史K线数据
- **功能描述**: 获取个股历史价格数据
- **输入参数**: 股票代码、开始日期、结束日期、复权类型
- **输出格式**: CSV/Markdown表格
- **数据源**: AkShare-东方财富 / Baostock
- **数据时效**: 日频，盘后更新
- **使用示例**:
  ```bash
  python scripts/stock_hist.py 600519 20260101 20260319
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| stock_quote_tx.py | 腾讯财经实时行情 | ✅ |
| stock_search_tx.py | 股票搜索（腾讯） | ✅ |
| stock_list.py | 股票列表筛选 | ✅ |
| stock_sector.py | 板块/行业分析 | ✅ |
| stock_capital.py | 资金流向分析 | ✅ |
| stock_lhb.py | 龙虎榜数据 | ✅ |
| stock_hist.py | 历史K线数据 | ✅ |
| stock_quote.py | 实时行情（AkShare备用） | ❌ |
| stock_search.py | 股票搜索（AkShare备用） | ❌ |

## 使用示例

### 命令行调用
```bash
# 实时行情
python scripts/stock_quote_tx.py 600519
python scripts/stock_quote_tx.py 000001

# 股票搜索
python scripts/stock_search_tx.py 茅台
python scripts/stock_search_tx.py 宁德时代

# 股票列表
python scripts/stock_list.py --market sh --limit 20

# 板块分析
python scripts/stock_sector.py 半导体
python scripts/stock_sector.py 新能源

# 资金流向
python scripts/stock_capital.py --limit 20

# 龙虎榜
python scripts/stock_lhb.py
```

### Python API调用
```python
from finclaw.core.data_fetcher import fetch_stock_realtime
from finclaw.core.data_annotator import format_stock_quote

# 获取实时行情
result = fetch_stock_realtime("600519")
if result.success:
    data = result.data
    # 格式化输出（自动带数据来源标注）
    output = format_stock_quote(
        stock_code=data['code'],
        stock_name=data['name'],
        price=data['price'],
        change=data['change'],
        change_pct=data['change_pct'],
        source=result.source
    )
    print(output)
```

## 数据来源标注规范

本Skill所有输出数据将按以下格式标注来源：

```markdown
---
📊 **数据来源**: 腾讯财经 / AkShare-东方财富
⏱️ **数据时间**: 2026-03-19 10:30:15
⚡ **获取延迟**: 234ms
🔗 **数据接口**: https://qt.gtimg.cn
🔧 **分析工具**: FinClaw v1.0
```

## 依赖要求

```
akshare>=1.10.0
pandas>=1.3.0
requests>=2.25.0
pyyaml>=5.4.0
```

## 环境变量

| 变量名 | 说明 | 必需 |
|:---|:---|:---:|
| `FINCLAW_DATA_SOURCE_CONFIG` | 数据源配置文件路径 | 否 |

## 错误处理

| 错误码 | 说明 | 处理建议 |
|:---|:---|:---|
| NETWORK_ERROR | 网络连接失败 | 检查网络，切换备用数据源 |
| INVALID_CODE | 股票代码无效 | 确认代码格式（6位数字） |
| DATA_NOT_FOUND | 数据不存在 | 检查是否为交易日/交易时间 |
| RATE_LIMIT | 请求频率过高 | 降低请求频率，添加延时 |

## 性能指标

| 指标 | 目标值 | 当前值 |
|:---|:---:|:---:|
| 实时行情延迟 | < 500ms | ~200ms |
| 可用性 | > 99% | 99.5% |
| 数据准确率 | > 98% | 99% |

## 股票代码格式

| 市场 | 代码格式 | 示例 |
|:---|:---|:---|
| 上海证券交易所 | 6xxxxx | 600519 (贵州茅台) |
| 深圳证券交易所 | 0xxxxx | 000001 (平安银行) |
| 创业板 | 3xxxxx | 300750 (宁德时代) |
| 科创板 | 688xxx | 688981 (中芯国际) |
| 北交所 | 8xxxxx/4xxxxx | 835185 (贝特瑞) |

## 热门板块

半导体、银行、白酒、新能源、医药、房地产、汽车、人工智能、芯片、5G、光伏、锂电池

## 注意事项

- 腾讯财经API无需注册，但可能有频率限制
- AkShare依赖东方财富，部分网络环境可能受限
- 龙虎榜数据仅在交易日盘后提供
- 所有数据仅供参考，不构成投资建议
- 历史数据支持前复权/后复权选择

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增数据来源强制标注 |
| 1.0.0 | 2026-03-12 | 初始版本 |

## 相关链接

- AkShare文档: https://www.akshare.xyz/
- 腾讯财经API: https://qt.gtimg.cn
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
