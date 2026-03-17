---
name: a-share-earnings-momentum
description: A股盈利动量/业绩趋势量化分析。当用户说"盈利动量"、"earnings momentum"、"业绩趋势"、"盈利加速"、"业绩改善"时触发。量化分析盈利变化趋势。支持formal和brief风格。
---
# A股盈利动量/业绩趋势量化分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取多期财务数据
### Step 2: 计算盈利动量指标
- 营收YoY加速度（本季YoY - 上季YoY）
- 净利润环比变化
- ROE变化趋势
- 毛利率变化方向
### Step 3: 盈利修正追踪
分析师预期的上调/下调趋势
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 盈利趋势 | 多季度趋势图 | 加速/减速 |
| 动量信号 | 各指标综合评分 | 盈利动量方向 |
默认风格：brief。
## 关键规则
1. 盈利动量是最有效的选股因子之一
2. 盈利加速比盈利增长更重要（二阶导>一阶导）
3. 分析师上调预期是盈利动量的领先信号
4. Q4季度性因素需特殊处理
5. 盈利动量和价格动量结合效果最好
