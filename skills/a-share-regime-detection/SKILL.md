---
name: a-share-regime-detection
description: A股市场状态/牛熊识别量化。当用户说"市场状态"、"regime"、"牛市还是熊市"、"现在是什么市"、"震荡市"、"趋势市"、"牛熊判断"时触发。基于 cn-stock-data 获取K线数据，量化识别当前市场状态。支持研报风格（formal）和快速分析风格（brief）。
---

# A股市场状态/牛熊识别量化

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取大盘数据
获取主要指数（上证/沪深300/创业板）K线 + 成交量 + 资金流。

### Step 2: 多维度状态判断
- **趋势维度**：MA20/MA60/MA120 排列（多头/空头/缠绕）
- **波动维度**：历史波动率分位（高波/低波）
- **成交维度**：成交量相对均值（放量/缩量）
- **情绪维度**：涨跌家数比/涨停数/跌停数

### Step 3: 状态分类
- 牛市（趋势上行+放量+情绪高涨）
- 熊市（趋势下行+缩量+情绪低迷）
- 震荡市（无明显趋势+量能一般）
- 转折期（指标矛盾+波动放大）

### Step 4: 历史状态回溯
标注过去 N 年的市场状态序列，统计各状态持续时间。

### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 当前状态 | 多维度评分 | 一句话判断 |
| 信号详情 | 各指标明细 | 关键信号 |
| 历史对比 | 类似状态历史 | 无 |

默认风格：brief。

## 关键规则
1. 单一指标判断市场状态不可靠——需多维度综合
2. 市场状态转换往往不是突变而是渐进的
3. A 股政策市特征明显——政策转向往往是状态转折点
4. 成交量是判断市场状态的领先指标
5. 不同状态适用不同策略（趋势市用动量，震荡市用均值回归）

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
