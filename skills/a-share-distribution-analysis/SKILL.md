---
name: a-share-distribution-analysis
description: A股收益率分布/统计特征分析。当用户说"收益率分布"、"distribution"、"正态检验"、"偏度"、"峰度"、"收益率统计"时触发。量化分析收益率分布特征。支持formal和brief风格。
---
# A股收益率分布/统计特征分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取K线收益率序列
### Step 2: 描述性统计
均值/中位数/标准差/偏度/峰度/最大值/最小值
### Step 3: 正态性检验
- Jarque-Bera检验
- Shapiro-Wilk检验
- QQ图分析
### Step 4: 分布拟合
拟合t分布/GED分布/混合正态，比较拟合优度
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 统计量 | 完整描述性统计 | 偏度/峰度 |
| 正态检验 | 多种检验结果 | 是否正态 |
| 分布拟合 | 最佳拟合分布 | 分布类型 |
默认风格：brief。
## 关键规则
1. A股收益率不服从正态分布——尖峰肥尾特征显著
2. 负偏度意味着下跌极端值更多——投资者面临左尾风险
3. 峰度>3说明极端收益出现频率高于正态预期
4. 分布假设影响VaR/期权定价等所有风险计算
5. 不同市值股票的分布特征差异大——小盘更尖峰
