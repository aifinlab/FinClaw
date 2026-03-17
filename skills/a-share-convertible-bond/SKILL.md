---
name: a-share-convertible-bond
description: A股可转债分析/转债策略/可转债估值与筛选。当用户提到"可转债"或"转债"就触发。关键词："可转债"、"转债"、"convertible bond"、"转股"、"转股价值"、"双低策略"、"强赎"、"XX转债怎么样"、"可转债打新"、"转债溢价率"、"转债分析"、"可转债筛选"、"转债到期收益率"、"YTM"、"下修"、"转债回售"。MUST USE when user mentions 可转债 or 转债 in any context — this is the ONLY skill for convertible bond analysis. 基于 efinance 可转债数据和 cn-stock-data 正股数据，分析转债估值（溢价率/到期收益率）、正股联动、强赎风险、转债策略。支持研报风格（formal）和快速解读风格（brief）。
---

# A股可转债分析助手

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 可转债实时行情（通过 akshare，cn-stock-data 不支持此命令）
# 方式1: akshare 集思录可转债数据（推荐，含溢价率/YTM/双低值等完整指标）
python -c "import akshare as ak; df=ak.bond_cb_jsl(); print(df.to_json(orient='records', force_ascii=False))"

# 方式2: efinance 可转债行情（备选，数据源可能不稳定）
python -c "import efinance as ef; df=ef.bond.get_realtime_quotes(); print(df.to_json(orient='records', force_ascii=False))"

# 正股行情（通过 cn-stock-data）
python "$SCRIPTS/cn_stock_data.py" quote --code [正股代码]

# 正股K线
python "$SCRIPTS/cn_stock_data.py" kline --code [正股代码] --freq daily --start [日期]

# 正股财务
python "$SCRIPTS/cn_stock_data.py" finance --code [正股代码]
```

补充：通过 web 搜索获取转股价调整公告、强赎公告等最新信息。

## Workflow

### Step 1: 确定分析模式

根据用户意图选择模式：
- **个债分析**：指定转债代码/名称 → 深度分析单只转债
- **策略筛选**：双低 / 低溢价 / 高YTM / 即将强赎 → 全市场筛选
- **市场全景**：转债市场整体估值水平、分布统计

### Step 2: 数据获取

1. 调用 `convertible_bond` 获取全市场转债行情（价格/溢价率/转股价值/到期收益率等）
2. 对目标转债，调用 `quote` / `kline` / `finance` 获取正股数据
3. 如需最新转股价或强赎公告，通过 web 搜索补充

### Step 3: 估值分析

核心指标计算（详见 references/convertible-bond-guide.md）：
- **转股价值** = 100 / 转股价 × 正股价
- **转股溢价率** = (转债价格 - 转股价值) / 转股价值 × 100%
- **纯债价值**：按同评级企业债收益率折现剩余现金流
- **到期收益率 YTM**：按到期赎回价计算的内部收益率
- **双低值** = 转债价格 + 转股溢价率 × 100（<130 为低估区间）

### Step 4: 风险分析

- **强赎风险**：正股连续30日中15日高于转股价130%（各转债具体条款可能不同）
- **下修可能性**：正股接近或低于转股价，发行人有动力下修
- **到期兑付风险**：正股基本面恶化，转债信用风险上升
- **流动性风险**：日均成交量过低，买卖价差大

### Step 5: 输出

根据风格要求输出：

| 维度 | formal（研报风格） | brief（快速解读） |
|------|-------------------|-------------------|
| 输出 | 完整转债研究报告 | 快速要点总结 |
| 估值分析 | 全面（纯债+期权+Greeks） | 核心指标（溢价率+YTM+双低值） |
| 正股分析 | 详细基本面分析 | 仅关键财务指标 |
| 策略建议 | 情景分析+多空因素 | 直接结论 |

默认风格：brief。用户要求"详细分析"/"研报"时切换为 formal。

## 关键规则

1. 可转债有"债底保护"但非零风险——需考虑信用风险（尤其 AA- 及以下评级）
2. 转股价可能下修——必须通过 web 搜索确认最新转股价，不能仅依赖历史数据
3. 强赎条款是最重要的风险点之一——临近强赎的转债价格通常锁定在130元附近
4. 可转债 T+0 交易，与正股 T+1 不同；无涨跌幅限制但有临时停牌机制
5. 策略筛选时，务必标注数据时间，提醒用户转债行情变化快
6. 计算指标时展示公式和中间步骤，确保可验证
