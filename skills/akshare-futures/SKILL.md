---
name: "akshare-futures"
description: "期货数据Skill - 提供商品期货、股指期货、持仓龙虎榜、期现价差分析 via AkShare/新浪财经"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-packages
        kind: pip
        packages: ["akshare", "pandas", "requests", "pyyaml"]
---

# SKILL.md - akshare-futures

## 技能信息

| 属性 | 内容 |
|:---|:---|
| **名称** | akshare-futures |
| **版本** | 1.1.0 |
| **分类** | 期货数据 |
| **状态** | ✅ 已上线 |
| **维护者** | FinClaw Core Team |
| **最后更新** | 2026-03-19 |

## 功能描述

期货数据Skill，提供商品期货、股指期货的实时行情、历史数据、持仓量龙虎榜、期现价差分析等。覆盖上期所、大商所、郑商所、中金所、能源中心五大交易所。

## 触发意图

### 主要触发词
- "期货"、"主力合约"、"持仓量"
- "螺纹钢"、"豆粕"、"原油"、"黄金"
- "多单"、"空单"、"龙虎榜"
- "基差"、"期现价差"
- "碳酸锂"、"股指期货"

### Few-shot 示例

| 用户输入 | 识别意图 | 调用函数 |
|:---|:---|:---|
| 螺纹钢期货行情 | futures_quote | futures_quote.py RB0 |
| 查询豆粕持仓龙虎榜 | futures_hold | futures_hold.py M0 |
| 原油期货多少钱？ | futures_quote | futures_quote.py SC0 |
| 股指期货走势 | futures_index | futures_quote.py IF0 |
| 期现价差分析 | futures_spread | futures_spread.py RB |

## 数据源配置

| 数据类型 | 主要来源 | 备用来源 | 认证要求 |
|:---|:---|:---|:---:|
| 期货实时行情 | 新浪财经 | AkShare | 无需 |
| 期货历史数据 | AkShare-东方财富 | - | 无需 |
| 持仓龙虎榜 | AkShare-交易所 | - | 无需 |
| 外盘期货 | AkShare-新浪 | - | 无需 |

## 支持的交易所

| 交易所 | 代码 | 主要品种 |
|:---|:---|:---|
| 上海期货交易所 | SHFE | 铜CU、铝AL、螺纹钢RB、黄金AU、原油SC |
| 大连商品交易所 | DCE | 豆粕M、铁矿石I、棕榈油P、玉米C |
| 郑州商品交易所 | ZCE | PTATA、甲醇MA、白糖SR、棉花CF |
| 中国金融期货交易所 | CFFEX | 沪深300IF、上证50IH、中证500IC、国债T |
| 上海国际能源交易中心 | INE | 原油期货SC、20号胶NR、低硫燃料油LU |

## 功能列表

### 1. 期货实时行情
- **功能描述**: 获取商品期货、股指期货实时行情
- **输入参数**: 合约代码（如RB0表示螺纹钢主力）
- **输出格式**: Markdown表格
- **数据源**: 新浪财经 API
- **数据时效**: 实时（交易时间内）
- **使用示例**:
  ```bash
  python scripts/futures_quote.py RB0  # 螺纹钢主力
  python scripts/futures_quote.py SC0  # 原油主力
  python scripts/futures_quote.py IF0  # 沪深300股指
  ```

### 2. 期货历史数据
- **功能描述**: 获取期货合约历史K线数据
- **输入参数**: 合约代码、开始日期、结束日期
- **输出格式**: CSV/Markdown表格
- **数据源**: AkShare-东方财富
- **数据时效**: 日频，盘后更新
- **使用示例**:
  ```bash
  python scripts/futures_hist.py RB2505 20250101 20260319
  ```

### 3. 持仓龙虎榜
- **功能描述**: 获取期货持仓量排行，识别主力动向
- **输入参数**: 合约代码
- **输出格式**: Markdown表格（多空持仓、增减变化）
- **数据源**: AkShare-交易所
- **数据时效**: 日频，盘后更新
- **使用示例**:
  ```bash
  python scripts/futures_hold.py RB2505  # 螺纹钢具体合约
  python scripts/futures_hold.py OI2501  # 菜籽油合约
  ```

### 4. 主力合约切换
- **功能描述**: 查询各品种主力合约及合约切换信息
- **输入参数**: 交易所代码（shfe/dce/zce/cffex/ine）
- **输出格式**: Markdown表格
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/futures_main.py shfe  # 上期所主力合约
  python scripts/futures_main.py dce   # 大商所主力合约
  ```

### 5. 期货板块监控
- **功能描述**: 监控各板块（金属/能源/化工/农产品）涨跌情况
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: 新浪财经
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/futures_board.py
  ```

### 6. 期现价差分析
- **功能描述**: 分析期货价格与现货价格的基差
- **输入参数**: 品种代码（如RB、M、AU）
- **输出格式**: Markdown报告
- **数据源**: AkShare
- **数据时效**: 日频
- **使用示例**:
  ```bash
  python scripts/futures_spread.py RB  # 螺纹钢期现价差
  python scripts/futures_spread.py M   # 豆粕期现价差
  ```

### 7. 外盘期货行情
- **功能描述**: 获取国际期货市场行情（原油、黄金、铜等）
- **输入参数**: 无
- **输出格式**: Markdown表格
- **数据源**: 新浪财经
- **数据时效**: 实时
- **使用示例**:
  ```bash
  python scripts/futures_global.py
  ```

## 脚本清单

| 脚本名 | 功能 | 入口点 |
|:---|:---|:---:|
| futures_quote.py | 期货实时行情 | ✅ |
| futures_hist.py | 期货历史数据 | ✅ |
| futures_hold.py | 持仓龙虎榜 | ✅ |
| futures_main.py | 主力合约切换 | ✅ |
| futures_board.py | 期货板块监控 | ✅ |
| futures_spread.py | 期现价差分析 | ✅ |
| futures_global.py | 外盘期货行情 | ✅ |

## 合约代码说明

### 主力合约表示法
| 表示法 | 含义 | 示例 |
|:---|:---|:---|
| `RB0` | 螺纹钢主力合约 | RB0 |
| `RB2505` | 螺纹钢2025年5月合约 | RB2505 |
| `M0` | 豆粕主力合约 | M0 |
| `SC0` | 原油主力合约 | SC0 |

### 常见品种代码
| 品种 | 代码 | 交易所 |
|:---|:---|:---|
| 螺纹钢 | RB | SHFE |
| 热轧卷板 | HC | SHFE |
| 铁矿石 | I | DCE |
| 焦煤 | JM | DCE |
| 焦炭 | J | DCE |
| 豆粕 | M | DCE |
| 棕榈油 | P | DCE |
| 原油 | SC | INE |
| 黄金 | AU | SHFE |
| 白银 | AG | SHFE |
| 铜 | CU | SHFE |
| 铝 | AL | SHFE |
| 沪镍 | NI | SHFE |
| 碳酸锂 | LC | GFEX |
| 工业硅 | SI | GFEX |

## 期现价差解读

| 价差状态 | 含义 | 市场判断 |
|:---|:---|:---|
| **正价差(Contango)** | 期货 > 现货 | 远期供应充足，仓储成本 |
| **逆价差(Backwardation)** | 期货 < 现货 | 即期供应紧张，需求旺盛 |
| **基差扩大** | 期现价差变大 | 供需失衡加剧 |
| **基差收窄** | 期现价差变小 | 期现趋于一致 |

## 数据来源标注规范

本Skill所有输出数据将按以下格式标注来源：

```markdown
---
📊 **数据来源**: 新浪财经 / AkShare-东方财富
⏱️ **数据时间**: 2026-03-19 10:30:15
📌 **交易所**: 上海期货交易所
🔗 **数据接口**: 新浪财经期货API
🔧 **分析工具**: FinClaw v1.0
⚠️ **风险提示**: 期货交易风险高，入市需谨慎
```

## 依赖要求

```
akshare>=1.10.0
pandas>=1.3.0
requests>=2.25.0
pyyaml>=5.4.0
```

## 交易时间

| 交易所 | 日盘 | 夜盘 |
|:---|:---|:---|
| 上期所/大商所/郑商所 | 09:00-11:30, 13:30-15:00 | 21:00-次日02:30（部分品种） |
| 中金所 | 09:30-11:30, 13:00-15:00 | 无 |
| 能源中心 | 09:00-11:30, 13:30-15:00 | 21:00-次日02:30 |

## 性能指标

| 指标 | 目标值 | 当前值 |
|:---|:---:|:---:|
| 实时行情延迟 | < 1s | ~500ms |
| 数据可用性 | > 95% | 98% |
| 数据准确率 | > 98% | 99% |

## 更新日志

| 版本 | 日期 | 变更内容 |
|:---|:---:|:---|
| 1.1.0 | 2026-03-19 | 符合FinClaw数据规范v1.0，新增触发意图、期现价差解读 |
| 1.0.0 | 2026-03-13 | 初始版本 |

## 相关链接

- AkShare文档: https://www.akshare.xyz
- 上期所: http://www.shfe.com.cn
- 大商所: http://www.dce.com.cn
- 郑商所: http://www.czce.com.cn
- 中金所: http://www.cffex.com.cn
- FinClaw数据规范: `finclaw/config/data_source_config.yaml`

---

*本Skill遵循 FinClaw 数据规范 v1.0 | 数据来源强制标注 | 禁止训练数据编造*
