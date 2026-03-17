---
name: a-share-autocorrelation
description: A股自相关/序列相关性/收益率自相关结构分析。当用户说"自相关"、"autocorrelation"、"序列相关"、"收益率预测性"、"动量还是反转"、"自相关系数"、"ACF"、"PACF"、"Ljung-Box"、"收益率是否可预测"、"随机游走检验"时触发。MUST USE when user asks about return autocorrelation, serial correlation tests, or whether a stock's returns are predictable. 量化分析收益率的自相关结构（ACF/PACF、Ljung-Box检验、随机游走检验）。支持formal和brief风格。
---
# A股自相关/序列相关性分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取K线收益率序列
### Step 2: 计算自相关函数(ACF)
lag 1-20的自相关系数
### Step 3: 偏自相关函数(PACF)
### Step 4: Ljung-Box检验
检验序列是否存在显著自相关
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| ACF/PACF | 完整图表 | 关键lag |
| 检验 | LB统计量+p值 | 有无自相关 |
| 含义 | 动量/反转判断 | 交易含义 |
默认风格：brief。
## 关键规则
1. 正自相关=动量效应（涨了还会涨）
2. 负自相关=反转效应（涨了会跌回）
3. A股日频负自相关较明显（T+1导致的隔日反转）
4. 周频/月频正自相关更显著（中期动量）
5. 自相关结构是时间序列策略的基础
