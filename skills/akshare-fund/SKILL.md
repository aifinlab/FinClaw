---
name: "akshare-fund"
description: "基金数据Skill - 提供ETF/LOF/开放式基金实时行情、净值查询、基金搜索 via 腾讯财经/AkShare"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["requests", "akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-fund

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-fund |
| **版本** | 1.1.0 |
| **分类** | 基金数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

基金数据Skill，提供ETF/LOF/开放式基金的实时行情、净值查询、基金搜索等服务。ETF/LOF支持实时行情，开放式基金提供每日净值。

## 触发意图

### 主要触发词
- "基金"、"净值"、"基金行情"
- "ETF"、"LOF"、"指数基金"
- "510300"、"159915"、"基金代码"
- "查询基金"、"基金收益"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 沪深300ETF多少钱？ | fund_realtime | fund_quote_tx.py 510300 |
| 查询创业板ETF净值 | fund_realtime | fund_quote_tx.py 159915 |
| 搜索白酒基金 | fund_search | fund_search_tx.py 白酒 |
| 有哪些科技ETF | fund_search | fund_search_tx.py 科技ETF |
| 华夏成长基金怎么样 | fund_realtime | fund_quote_tx.py 000001 |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| ETF/LOF实时行情 | 腾讯财经 | 新浪财经 | 无需 |
| 基金净值 | AkShare-东方财富 | - | 无需 |
| 基金搜索 | 腾讯财经 | - | 无需 |
| 基金排行 | AkShare-东方财富 | - | 无需 |

## 功能列表

### 1. 基金实时行情
- **功能描述**: 获取ETF/LOF实时行情，开放式基金最新净值
- **输入参数**: 基金代码（如 510300, 159915）
- **输出格式**: Markdown表格（净值、涨跌、成交额等）
- **数据源**: 腾讯财经 API
- **数据时效**: ETF/LOF实时（延迟<1秒），开放式基金日频
- **使用示例**:
  ```bash
  python scripts/fund_quote_tx.py 510300
  python scripts/fund_quote_tx.py 000001
  ```

### 2. 基金搜索
- **功能描述**: 根据名称/拼音搜索基金代码
- **输入参数**: 基金名称关键词（如"沪深300"、"白酒"、"科技ETF"）
- **输出格式**: 匹配基金列表（代码、名称、类型）
- **数据源**: 腾讯财经 API
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/fund_search_tx.py 白酒
  python scripts/fund_search_tx.py 科技ETF
  python scripts/fund_search_tx.py 沪深300
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| fund_quote_tx.py | 基金实时行情/净值（腾讯） | ✅ |
| fund_search_tx.py | 基金搜索（腾讯） | ✅ |

## 使用示例

### 命令行调用
```bash
# 查询ETF实时行情
python scripts/fund_quote_tx.py 510300
python scripts/fund_quote_tx.py 159915

# 查询开放式基金净值
python scripts/fund_quote_tx.py 000001

# 搜索基金
python scripts/fund_search_tx.py 白酒
python scripts/fund_search_tx.py 新能源
```

### Python API调用
```python
from finclaw.core.data_annotator import annotate_data

# 获取基金数据后标注来源
fund_data = {
    "基金名称": "华泰柏瑞沪深300ETF",
    "基金代码": "510300",
    "最新净值": "3.854",
    "日涨跌": "+0.52%"
}
output = annotate_data(fund_data, source="tencent_finance")
print(output)
```

## 数据来源标注规范

本Skill所有输出数据将按以下格式标注来源：

```markdown
---
📊 **数据来源**: 腾讯财经
⏱️ **数据时间**: 2026-03-19 10:30:15
⚡ **获取延迟**: 180ms
🔗 **数据接口**: https://qt.gtimg.cn
🔧 **分析工具**: FinClaw v1.0
```

## 依赖要求

```
requests>=2.25.0
akshare>=1.10.0
pandas>=1.3.0
pyyaml>=5.4.0
```

## 基金代码格式

| 类型 | 代码格式 | 示例 |
|:---|:---|:---|
| ETF | 51xxxx/15xxxx/56xxxx | 510300 (沪深300ETF) |
| LOF | 16xxxx | 160106 (南方高增) |
| 开放式基金 | 000xxx/001xxx | 000001 (华夏成长) |
| 货币基金 | 如余额宝等 | 000198 (天弘余额宝) |

## 热门ETF

| ETF名称 | 代码 | 跟踪指数 |
|:---|:---|:---|
| 沪深300ETF | 510300 | 沪深300指数 |
| 创业板ETF | 159915 | 创业板指数 |
| 科创50ETF | 588000 | 科创50指数 |
| 中证500ETF | 510500 | 中证500指数 |
| 芯片ETF | 512760 | 半导体指数 |
| 新能源ETF | 516160 | 新能源指数 |

## 注意事项

- ETF/LOF有实时行情，交易时间内可实时跟踪
- 开放式基金每日收盘后更新净值（约18:00-20:00）
- 货币基金显示万份收益和7日年化收益率
- 所有数据仅供参考，不构成投资建议

## 性能指标

| 指标 | 目标值 | 当前值 |
|:---|:---:|:---:|
| ETF行情延迟 | < 500ms | ~200ms |
| 可用性 | > 99% | 99.5% |
| 数据准确率 | > 98% | 99% |

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增数据来源强制标注 |
| 1.0.0 | 2026-03-12 | 初始版本 |

## 相关链接

- 腾讯财经API: https://qt.gtimg.cn
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
