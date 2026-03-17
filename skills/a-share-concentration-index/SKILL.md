---
name: a-share-concentration-index
description: A股市场集中度/筹码集中度分析。当用户说"集中度"、"concentration"、"筹码集中"、"HHI"、"CR10"、"龙头占比"时触发。量化分析市场或行业集中度。支持formal和brief风格。
---
# A股市场集中度/筹码集中度分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取行业/市场数据
### Step 2: 计算集中度指标
- CR_n: 前N名市值/营收占比
- HHI: 赫芬达尔指数 = Σ(s_i²)
- 基尼系数: 收益率/市值分布的不均匀度
### Step 3: 集中度变化趋势
历史集中度时序变化
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 集中度指标 | CR5/10/20+HHI | CR5 |
| 趋势 | 历史变化序列 | 升/降 |
默认风格：brief。
## 关键规则
1. 集中度上升→龙头溢价→适合集中持仓
2. 集中度下降→百花齐放→适合分散持仓
3. A股近年行业集中度趋势上升（供给侧改革后）
4. 筹码集中度可用股东人数变化衡量
5. HHI > 2500为高度集中
