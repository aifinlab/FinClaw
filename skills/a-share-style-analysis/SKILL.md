---
name: a-share-style-analysis
description: A股风格分析/Sharpe风格归因。当用户说"风格分析"、"style analysis"、"Sharpe风格"、"风格暴露"、"偏大盘还是小盘"时触发。量化分析基金或组合的风格暴露。支持formal和brief风格。
---
# A股风格分析/Sharpe风格归因
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取组合/基金净值+风格指数
### Step 2: Sharpe风格分析
约束回归: R_p = Σ(w_i × R_style_i) + ε
约束: w_i ≥ 0, Σw_i = 1
### Step 3: 风格漂移检测
滚动窗口分析风格权重变化
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 风格权重 | 完整分解 | 主要风格 |
| 风格漂移 | 时序变化图 | 是否漂移 |
默认风格：brief。
## 关键规则
1. Sharpe风格分析用约束二次规划（权重非负且和为1）
2. 风格指数选择影响结果——需覆盖主要风格维度
3. 风格漂移是基金评估的重要维度
4. A股常用风格维度：大盘价值/大盘成长/小盘价值/小盘成长
5. R² > 0.9 说明风格指数解释力强

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
