---
name: a-share-dragon-tiger
description: A股龙虎榜分析/游资追踪。当用户说"龙虎榜"、"游资"、"营业部"、"席位"、"涨停分析"、"dragon tiger"、"谁在买"、"机构席位"、"游资大佬"、"XX上龙虎榜了吗"时触发。基于 efinance 龙虎榜数据，分析个股上榜原因、买卖席位、机构vs游资博弈、近期龙虎榜活跃股。支持券商研报风格（formal）和快速解读风格（brief）。不适用于北向资金分析（用 a-share-northbound）或基金持仓（用 a-share-fund-holding）。
---

# A股龙虎榜分析助手

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 龙虎榜数据（通过 akshare，cn-stock-data 不支持此命令）
# 方式1: akshare 龙虎榜明细（推荐，数据最全）
python -c "import akshare as ak; df=ak.stock_lhb_detail_em(start_date='YYYYMMDD', end_date='YYYYMMDD'); print(df.to_json(orient='records', force_ascii=False))"

# 方式2: efinance 龙虎榜（备选）
python -c "import efinance as ef; df=ef.stock.get_daily_billboard(); print(df.to_json(orient='records', force_ascii=False))"

# 个股行情（通过 cn-stock-data）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]

# K线（看上榜前后走势）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]

# 资金流向
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE]
```

补充：通过 web 搜索确认席位背后的游资/机构身份。

## Workflow

### Step 1: 确定分析范围

根据用户意图分类：
- **个股龙虎榜解读**：某只股票的龙虎榜明细分析
- **当日龙虎榜全览**：当日所有上榜个股概览
- **特定席位追踪**：某营业部/机构的近期操作记录

### Step 2: 数据获取

获取龙虎榜明细（买卖前5席位、金额、占比）+ 个股行情 + 近期K线。多只股票时并行获取。

### Step 3: 席位分析

- 区分机构专用席位 vs 知名游资营业部 vs 普通席位
- 分析买卖力量对比（净买入/净卖出）
- 识别"一日游"模式 vs 持续买入模式
- 知名游资/机构身份不确定时，用 web 搜索确认

> 详见 [references/dragon-tiger-guide.md](references/dragon-tiger-guide.md) 中的席位类型识别和常见模式。

### Step 4: 关联分析

- **上榜原因**：涨跌停/振幅/换手率异常
- **资金流向对比**：龙虎榜净买入方向 vs 当日主力资金流向是否一致
- **上榜频率**：近期频繁上榜 = 活跃博弈信号

### Step 5: 输出

根据风格生成报告：

| 维度 | formal | brief |
|------|--------|-------|
| 输出格式 | 完整龙虎榜报告 | 快速要点 |
| 席位分析 | 逐席详细分析 | 仅标注机构/知名游资 |
| 统计 | 净买卖汇总+历史上榜统计 | 仅净买卖方向 |
| 结论 | 客观陈述（"机构净买入X亿"） | 可加判断 |

默认风格：brief。用户要求"详细分析"/"出报告"时用 formal。

## 关键规则

1. **T+1 延迟**：龙虎榜数据于当日收盘后公布，分析时注明数据日期
2. **机构标注**：机构专用席位必须特别标注，区别于普通营业部
3. **游资识别**：知名游资营业部（赵老哥、炒股养家等常驻席位）可通过 web 搜索确认
4. **不做跟庄建议**：只陈述席位买卖事实，不建议"跟随买入"
5. **数据局限**：仅公布前5大买卖席位，不反映全部交易
