---
name: a-share-gap-analysis
description: A股跳空缺口分析/缺口策略。当用户说"缺口"、"gap"、"跳空"、"缺口分析"、"缺口回补"、"跳空高开"、"跳空低开"时触发。量化分析跳空缺口特征和交易含义。支持formal和brief风格。
---
# A股跳空缺口分析/缺口策略
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取K线数据
### Step 2: 识别缺口
- 向上缺口: 今日最低 > 昨日最高
- 向下缺口: 今日最高 < 昨日最低
### Step 3: 缺口分类
- 普通缺口（盘整区间内，易回补）
- 突破缺口（离开整理区间）
- 持续缺口（趋势中段加速）
- 衰竭缺口（趋势末端，反转信号）
### Step 4: 缺口回补分析
历史上同类缺口的回补概率和回补时间
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 缺口列表 | 历史缺口全表 | 近期缺口 |
| 分类 | 缺口类型判断 | 类型+含义 |
| 回补统计 | 回补概率+时间 | 是否回补 |
默认风格：brief。
## 关键规则
1. A股缺口回补率较高（约70-80%最终回补）
2. 突破缺口回补概率最低——最有交易价值
3. 衰竭缺口是反转信号——需及时止盈/止损
4. 连续多个缺口通常意味着极端行情
5. 涨跌停造成的缺口需特殊处理

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
