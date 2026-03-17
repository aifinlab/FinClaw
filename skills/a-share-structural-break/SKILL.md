---
name: a-share-structural-break
description: A股结构变点检测/趋势拐点识别。当用户说"结构变点"、"structural break"、"拐点"、"趋势改变"、"什么时候变了"、"Chow检验"时触发。量化检测价格序列的结构性变化。支持formal和brief风格。
---
# A股结构变点检测/趋势拐点识别
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取K线时间序列
### Step 2: 变点检测方法
- CUSUM检验（累积和）
- Chow检验（已知候选断点）
- Bai-Perron多断点检验
### Step 3: 断点前后对比
比较断点前后的均值/波动率/趋势斜率变化
### Step 4: 归因分析
关联断点时间与重大事件（政策/业绩/市场）
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 断点检测 | 多方法+统计检验 | 最近断点 |
| 前后对比 | 均值/波动率变化 | 趋势变了吗 |
| 归因 | 事件关联分析 | 可能原因 |
默认风格：brief。
## 关键规则
1. 结构断点通常对应重大事件（政策/业绩/市场危机）
2. 多种检验方法一致的断点更可靠
3. 断点检测有事后偏差——实时判断更难
4. 波动率断点往往先于均值断点
5. 断点后的新均衡状态可能持续较长时间
