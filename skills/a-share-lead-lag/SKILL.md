---
name: a-share-lead-lag
description: A股领先滞后关系/板块传导分析。当用户说"领先滞后"、"lead lag"、"谁先涨"、"传导"、"板块传导"、"龙头带动"时触发。量化分析股票/板块间的领先滞后关系。支持formal和brief风格。
---
# A股领先滞后关系/板块传导分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取多标的K线
### Step 2: 交叉相关分析
计算标的A在t期收益率与标的B在t+k期收益率的相关性（k=-5到+5）
### Step 3: Granger因果检验
检验A是否Granger因果引起B（或反向）
### Step 4: 领先滞后图谱
构建多标的间的领先-滞后关系网络
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 相关矩阵 | 多lag完整矩阵 | 最强领先关系 |
| 因果检验 | Granger检验结果 | 领先/滞后天数 |
| 关系图谱 | 完整网络图 | Top 3领先者 |
默认风格：brief。
## 关键规则
1. 领先滞后关系可能不稳定——需滚动窗口验证
2. 相关性≠因果——Granger检验也只是统计因果
3. A股中上游→下游传导较明显（如铜→电线电缆）
4. 大盘股往往领先小盘股1-2日
5. 北向资金动向常领先A股1-3日
