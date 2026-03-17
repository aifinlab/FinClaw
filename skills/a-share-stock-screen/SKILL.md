---
name: a-share-stock-screen
description: A股量化选股/股票筛选器。当用户说"选股"、"筛选"、"量化选股"、"stock screen"、"找机会"、"什么股票值得关注"、"帮我选几只股票"、"符合XX条件的股票"时触发。支持多因子筛选（PE/PB/ROE/净利润增速/北向资金等）、行业板块筛选、自定义条件组合。通过 cn-stock-data 获取全市场数据进行量化筛选，输出候选股票列表。支持投资建议书风格（formal）和个人备选池风格（brief）。不适用于个股深度分析（用 a-share-earnings-analysis）或可比公司估值对标（用 a-share-comps）。
---

# A 股量化选股

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 全市场实时行情（含市值、PE、换手率等）
python "$SCRIPTS/cn_stock_data.py" quote --code [逗号分隔的代码列表]

# 个股财务指标
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]

# 北向资金
python "$SCRIPTS/cn_stock_data.py" north_flow

# 资金流向
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE]
```

**使用 scripts/screen_engine.py 进行批量筛选**：
```bash
python $SKILLS_ROOT/a-share-stock-screen/scripts/screen_engine.py \
  --min-roe 15 --max-pe 30 --min-profit-growth 20 --top 20
```

## Workflow

### Step 1: 明确筛选条件

如果用户给出了明确条件（如"PE < 20 且 ROE > 15%"），直接使用。
如果用户给出模糊需求（如"帮我选几只好股票"），使用默认策略：

**默认多因子策略**（参见 `references/default-factors.md`）：
- ROE > 15%（盈利能力好）
- 净利润同比增速 > 20%（成长性好）
- 资产负债率 < 60%（财务健康）
- PE < 行业中位数（估值合理）
- 近 30 日主力净流入 > 0（资金认可）

用户也可以选择预设策略：
- **价值策略**: 低 PE + 低 PB + 高股息率
- **成长策略**: 高收入增速 + 高利润增速 + 合理 PE
- **GARP 策略**: PEG < 1（PE/净利润增速 < 1）
- **北向资金策略**: 近期北向资金持续净买入

### Step 2: 数据获取与筛选

运行 screen_engine.py 或通过 cn-stock-data 逐步获取数据：
1. 获取全市场股票列表（通过 adata 的 all_code）
2. 获取各股财务指标
3. 应用筛选条件
4. 按综合得分排序

**注意**：全市场筛选数据量大，优先使用 screen_engine.py 脚本批量处理。
如果脚本不可用，可分批次通过 cn-stock-data 获取重点行业数据。

### Step 3: 结果整理

对筛选出的 Top 10-20 只股票：
- 列出关键指标对比表
- 每只股票附 1-2 句概要（行业 + 核心亮点）
- 按综合评分排序

### Step 4: 输出

根据风格要求输出：
- formal: 完整的投资建议书格式，含策略说明、筛选方法论、详细对比表
- brief: 简洁候选列表，直奔数据

### Step 5: 可选深入

用户可以要求对列表中任一只做深度分析，此时转交 a-share-earnings-analysis skill。

## 风格说明

| 维度 | formal（投资建议书） | brief（个人备选池） |
|------|-------------------|--------------------|
| 篇幅 | 3-5 页 | 1 页 |
| 策略说明 | 详述筛选方法论和因子选择理由 | 一句话策略说明 |
| 对比表 | 完整（10+ 列指标） | 精简（5-6 列关键指标） |
| 个股概要 | 每只 3-5 句 | 每只 1 句 |
| 免责声明 | 需要 | 不需要 |

## 输出格式

### 对比表必含字段
| 代码 | 名称 | 行业 | 市值(亿) | PE(TTM) | PB | ROE(%) | 净利润YoY(%) | 毛利率(%) | 评分 |

### formal 模式额外字段
| 资产负债率(%) | 经营现金流/利润 | 北向持仓变化 | 近30日涨跌幅(%) |
