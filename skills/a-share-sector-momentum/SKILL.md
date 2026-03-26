---
name: a-share-sector-momentum
description: A股板块动量/行业轮动动量策略。当用户说"板块动量"、"sector momentum"、"哪个板块强"、"行业动量"、"追强势板块"时触发。量化分析板块动量排序。支持formal和brief风格。
---
# A股板块动量/行业轮动动量策略
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取各行业指数K线
### Step 2: 计算板块动量
- 过去N日涨跌幅排名（N=5/10/20/60）
- 动量得分 = 加权多周期涨幅
### Step 3: 动量持续性分析
- 强势板块继续强势的概率
- 动量衰减速度（各周期）
### Step 4: 轮动策略回测
选Top K强势板块持有M日的历史表现
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 板块排名 | 多周期完整排名 | Top/Bottom 5 |
| 动量分析 | 动量持续性统计 | 当前强弱 |
| 策略回测 | 完整回测结果 | 推荐板块 |
默认风格：brief。
## 关键规则
1. 板块动量在A股比个股动量更稳定
2. 最强板块往往在达到极端后反转
3. 避免追入已连涨超过3周的板块（动量衰减）
4. 北向资金流向可辅助判断板块动量持续性
5. 板块动量与市场状态有关——趋势市动量更强

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
