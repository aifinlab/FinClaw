# 高频波动率/已实现方差分析助手参考指南

## 一、已实现方差理论

### 1.1 RV估计方法
- Andersen & Bollerslev (1998): 已实现波动率的开创性工作
- Barndorff-Nielsen & Shephard (2002): 二次幂变差与跳跃检验
- Hansen & Lunde (2006): 已实现核估计量
- Zhang, Mykland & Ait-Sahalia (2005): 两尺度RV

### 1.2 A股高频波动率
- A股最优采样频率约5分钟(经验研究)
- 午间休市(1.5小时)需要特殊处理
- 涨跌停时RV估计失真(价格被截断)
- A股RV通常高于成熟市场同类股票

