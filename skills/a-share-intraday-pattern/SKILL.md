---
name: a-share-intraday-pattern
description: A股日内模式/分时走势量化分析。当用户说"日内模式"、"intraday"、"分时"、"盘中走势"、"几点涨"、"尾盘规律"时触发。量化分析A股日内交易模式。支持formal和brief风格。
---
# A股日内模式/分时走势量化分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取分钟级K线
### Step 2: 日内收益率分布
各时段（开盘/早盘/午盘/尾盘）的平均涨跌幅
### Step 3: 日内量能分布
各时段成交量占比和变化规律
### Step 4: 日内模式识别
- U型成交量（开盘尾盘放量，盘中缩量）
- 尾盘效应（最后30分钟异常）
- 午后效应
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 时段分析 | 各时段详细统计 | 关键时段 |
| 量能分布 | 分时量能图 | U型特征 |
| 规律总结 | 历史统计验证 | 今日模式 |
默认风格：brief。
## 关键规则
1. A股开盘30分钟和收盘30分钟波动最大
2. 集合竞价（9:15-9:25）反映隔夜消息消化
3. 午后1:00-1:30常有政策/消息发布影响
4. 尾盘集合竞价（14:57-15:00）可能被操纵
5. 日内模式在不同市场状态下会变化

## 使用示例

### 示例 1: 基本使用

```python
# 调用 skill
result = run_skill({
    "param1": "value1",
    "param2": "value2"
})
```

### 示例 2: 命令行使用

```bash
python scripts/run_skill.py --input data.json
```
