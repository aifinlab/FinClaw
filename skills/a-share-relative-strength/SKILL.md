---
name: a-share-relative-strength
description: A股相对强弱/RS分析。当用户说"相对强弱"、"relative strength"、"RS"、"XX比大盘强吗"、"跑赢跑输"时触发。量化分析个股/板块相对大盘的强弱。支持formal和brief风格。
---
# A股相对强弱/RS分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取标的+基准K线
### Step 2: 计算RS
RS = 标的价格 / 基准价格（标准化为100起点）
### Step 3: RS趋势分析
- RS上升→跑赢大盘
- RS下降→跑输大盘
- RS拐点→相对强弱切换
### Step 4: RS排名
全市场/行业内RS排名
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| RS曲线 | 完整RS时序 | 当前RS方向 |
| RS排名 | 全市场百分位 | 强/弱 |
默认风格：brief。
## 关键规则
1. RS是趋势交易的核心指标——买强卖弱
2. RS新高往往先于股价新高
3. RS持续走弱的股票即使便宜也需谨慎
4. 板块RS比个股RS更稳定
5. RS结合绝对趋势效果更好

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
