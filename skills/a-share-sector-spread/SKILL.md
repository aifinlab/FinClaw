---
name: a-share-sector-spread
description: A股板块价差/行业估值差分析。当用户说"板块价差"、"sector spread"、"行业估值差"、"板块分化"、"分化有多大"时触发。量化分析板块间价差和估值差异。支持formal和brief风格。
---
# A股板块价差/行业估值差分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取各行业估值和K线数据
### Step 2: 计算板块价差
- 行业间估值差（PE/PB差值）
- 行业间涨跌幅差
- 历史价差分位数
### Step 3: 分化程度分析
- 行业收益率离散度（标准差）
- 行业估值离散度
- 与历史分化程度对比
### Step 4: 均值回归信号
过度分化→可能反转
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 价差 | 完整行业价差矩阵 | 最大价差 |
| 分化度 | 离散度时序 | 当前分化水平 |
| 回归信号 | 历史分位分析 | 是否过度分化 |
默认风格：brief。
## 关键规则
1. 行业估值差扩大到极端时倾向回归
2. 分化程度与市场结构化行情正相关
3. 过度分化=板块轮动机会
4. A股行业PE差异巨大——需用PB或PS辅助对比
5. 新兴行业vs传统行业的估值差有趋势性成分
