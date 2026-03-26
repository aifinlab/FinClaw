---
name: a-share-signal-backtest
description: A股交易信号回测/策略验证。当用户说"信号回测"、"signal backtest"、"这个信号准不准"、"信号验证"、"交易信号回测"时触发。量化回测特定交易信号的历史表现。支持formal和brief风格。
---
# A股交易信号回测/策略验证
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 定义交易信号
明确入场/出场条件
### Step 2: 获取历史K线
### Step 3: 生成信号序列
标记每个交易日的信号（买入/卖出/持有）
### Step 4: 回测绩效
- 胜率、盈亏比、最大回撤
- 年化收益率、夏普比率
- 信号频率、平均持有期
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 绩效 | 完整回测报告 | 胜率+夏普 |
| 交易明细 | 每笔交易记录 | 统计摘要 |
| 稳健性 | 分年度/参数敏感性 | 是否稳健 |
默认风格：brief。
## 关键规则
1. 回测不代表未来——过拟合是最大风险
2. 样本外验证至关重要——至少留20%数据
3. 考虑交易成本（A股约0.15%单边）和滑点
4. T+1限制需在回测中体现——当日信号次日执行
5. 参数敏感性分析：参数微调后收益不应剧变

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
