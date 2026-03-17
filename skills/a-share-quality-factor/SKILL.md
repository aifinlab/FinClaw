---
name: a-share-quality-factor
description: A股质量因子/盈利质量量化分析。当用户说"质量因子"、"quality factor"、"盈利质量"、"高质量"、"ROE质量"、"应计"时触发。量化构建和分析质量因子。支持formal和brief风格。
---
# A股质量因子/盈利质量量化分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取财务数据
### Step 2: 构建质量因子
- 盈利能力: ROE/ROIC/毛利率
- 盈利稳定性: ROE标准差(过去5年)
- 应计质量: (净利润-经营现金流)/总资产
- 资产负债质量: 负债率/流动比率
### Step 3: 因子检验
IC/IR分析、分组回测
### Step 4: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 因子值 | 多维度质量评分 | 综合质量分 |
| 因子效果 | IC/IR+分组收益 | 因子有效性 |
默认风格：brief。
## 关键规则
1. 质量因子在熊市表现更突出（防御性）
2. 低应计比例=高盈利质量（现金利润占比高）
3. ROE高但自由现金流差→质量存疑
4. 质量因子与价值因子结合效果更好
5. A股财务造假风险需特别关注应计异常
