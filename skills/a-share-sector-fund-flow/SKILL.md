---
name: a-share-sector-fund-flow
description: A股行业资金流向/板块主力资金分析。当用户说"行业资金流"、"sector fund flow"、"板块资金"、"哪个行业有资金流入"、"资金流去哪个行业"时触发。量化分析各行业资金流向。支持formal和brief风格。
---
# A股行业资金流向/板块主力资金分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取各行业资金流向数据
### Step 2: 标准化处理
按行业市值归一化资金流入（每万亿市值净流入）
### Step 3: 资金流动量
- 近5日均值 vs 近20日均值
- 排名变化追踪
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 行业排名 | 全行业资金流表 | Top/Bottom 5 |
| 动量分析 | 资金流动量排名 | 加速流入板块 |
默认风格：brief。
## 关键规则
1. 单日资金流噪音大——至少用3-5日平均
2. 主力资金定义各平台不统一——注意口径差异
3. 资金流入≠涨——可能是高位承接
4. 行业轮动往往资金先行、股价后动
5. 融资余额变化是行业资金流的辅助指标
