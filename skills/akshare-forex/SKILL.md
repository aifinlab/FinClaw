---
name: "akshare-forex"
description: "外汇数据Skill - 提供全球主要货币对汇率、中国银行牌价 via AkShare/中国银行"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "pyyaml"]
---

# SKILL.md - akshare-forex

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-forex |
| **版本** | 1.1.0 |
| **分类** | 外汇数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

外汇数据Skill，提供全球主要货币对（美元兑人民币、欧元、日元等）的实时汇率、中国银行外汇牌价、美元指数等数据。

## 触发意图

### 主要触发词
- "汇率"、"美元兑人民币"、"美元"
- "人民币"、"贬值"、"升值"
- "外汇"、"外币"、"兑换"
- "美元指数"、"欧元"、"日元"
- "中国银行牌价"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 美元兑人民币多少？ | forex_quote | forex_quote.py |
| 今天汇率多少？ | forex_quote | forex_quote.py |
| 中国银行外汇牌价 | forex_boc | forex_boc.py |
| 美元指数走势 | forex_dxy | forex_quote.py --index |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 汇率行情 | AkShare | - | 无需 |
| 银行牌价 | 中国银行 | - | 无需 |
| 美元指数 | AkShare | - | 无需 |

## 支持的货币对

### 主要货币对
| 货币对 | 代码 | 说明 |
|:---|:---|:---|
| USD/CNY | USDCNY | 美元兑人民币（在岸） |
| USD/CNH | USDCNH | 美元兑人民币（离岸） |
| EUR/CNY | EURCNY | 欧元兑人民币 |
| JPY/CNY | JPYCNY | 100日元兑人民币 |
| GBP/CNY | GBPCNY | 英镑兑人民币 |
| HKD/CNY | HKDCNY | 港币兑人民币 |
| EUR/USD | EURUSD | 欧元兑美元 |
| USD/JPY | USDJPY | 美元兑日元 |
| GBP/USD | GBPUSD | 英镑兑美元 |
| AUD/USD | AUDUSD | 澳元兑美元 |

### 美元指数成分
| 货币 | 权重 |
|:---|:---:|
| 欧元 EUR | 57.6% |
| 日元 JPY | 13.6% |
| 英镑 GBP | 11.9% |
| 加元 CAD | 9.1% |
| 瑞典克朗 SEK | 4.2% |
| 瑞士法郎 CHF | 3.6% |

## 功能列表

### 1. 汇率行情
- **功能描述**: 获取全球主要货币对实时汇率
- **输入参数**: 货币对（可选）
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/forex_quote.py
  python scripts/forex_quote.py --pair USDCNY
  python scripts/forex_quote.py --index  # 美元指数
  ```

### 2. 中国银行牌价
- **功能描述**: 获取中国银行外汇牌价（现汇买入/卖出、现钞买入/卖出）
- **输入参数**: 无（全币种）或特定货币
- **输出格式**: Markdown表格
- **数据源**: 中国银行
- **数据时效**: 日频（工作日更新）
- **使用示例**:
  ```bash
  python scripts/forex_boc.py
  python scripts/forex_boc.py --currency USD
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| forex_quote.py | 汇率行情 | ✅ |
| forex_boc.py | 中国银行牌价 | ✅ |

## 汇率解读

### 美元兑人民币
| 汇率水平 | 数值 | 影响 |
|:---|:---:|:---|
| 强美元 | >7.3 | 出口企业受益，进口成本上升 |
| 正常区间 | 6.9-7.3 | 正常波动 |
| 强人民币 | <6.9 | 进口成本下降，出口承压 |

### 汇率变动影响
| 变动 | 对出口 | 对进口 | 对A股 |
|:---|:---:|:---:|:---:|
| 人民币贬值 | 利好 | 利空 | 出口股涨，航空股跌 |
| 人民币升值 | 利空 | 利好 | 航空股涨，出口股跌 |

## 数据来源标注规范

本Skill所有输出数据将按以下格式标注来源：

```markdown
---
📊 **数据来源**: AkShare / 中国银行
⏱️ **数据时间**: 2026-03-19 10:30:15
📌 **基准货币**: 人民币(CNY)
🔗 **原始来源**: 中国银行外汇牌价
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

## 相关链接

- AkShare文档: https://www.akshare.xyz
- 中国银行外汇牌价: http://www.boc.cn/sourcedb/whpj/
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
