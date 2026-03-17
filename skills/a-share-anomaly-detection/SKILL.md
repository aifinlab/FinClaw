---
name: a-share-anomaly-detection
description: A股量价异常检测/异动监控。当用户说"异常检测"、"异动"、"anomaly"、"量价异常"、"异常波动"、"XX有异动"时触发。量化检测股价和成交量异常。支持formal和brief风格。
---

# A股量价异常检测/异动监控

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取K线数据
### Step 2: 统计异常检测
- 收益率Z-score = (r - μ) / σ（|Z| > 2 为异常）
- 成交量Z-score（|Z| > 2 为异常放量/缩量）
- 振幅异常：日振幅 > 历史均值 + 2σ
### Step 3: 模式异常检测
- 量价背离：价涨量缩 或 价跌量增
- 尾盘异动：最后30分钟涨跌 > 日涨跌的50%
- 连续异常：连续3日同方向异常
### Step 4: 异常归因
关联近期公告/新闻/资金流，尝试解释异常原因
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 异常信号 | 完整异常事件列表 | 最新异常 |
| 统计分析 | Z-score+分布 | 异常等级 |
| 归因 | 可能原因分析 | 一句话 |
默认风格：brief。

## 关键规则
1. 异常不等于机会——可能是风险信号
2. 统计异常需结合基本面/消息面综合判断
3. A股信息泄露常见——异常可能先于公告
4. 单日异常可能是噪音——连续异常更值得关注
5. 成交量异常通常比价格异常更有预测价值
