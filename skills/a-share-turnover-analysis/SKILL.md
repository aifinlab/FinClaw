---
name: a-share-turnover-analysis
description: A股换手率分析/筹码松动分析。当用户说"换手率"、"turnover"、"筹码"、"换手率异常"、"筹码松动"时触发。量化分析换手率变化含义。支持formal和brief风格。
---
# A股换手率分析/筹码松动分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取K线+换手率数据
### Step 2: 换手率统计
- 当日换手率 vs 历史均值/中位数
- 换手率Z-score
- 换手率分位数
### Step 3: 量价配合分析
- 高换手+涨: 活跃看多
- 高换手+跌: 恐慌/出货
- 低换手+涨: 控盘/惜售
- 低换手+跌: 无人问津
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 换手统计 | 完整统计+分布 | Z-score |
| 量价配合 | 历史模式分析 | 当日模式 |
默认风格：brief。
## 关键规则
1. 换手率比成交量更具可比性（剔除流通盘差异）
2. 不同板块换手率中枢差异大——需行业内对比
3. 连续放量换手>15%: 可能是顶部信号
4. 底部缩量换手<1%: 可能见底
5. 新股/次新股换手率天然偏高——不可直接对比
