# 日内波动率/已实现波动率分析助手参考指南

## 一、已实现波动率理论

### 1.1 RV估计方法
- Andersen & Bollerslev (1998): 高频数据已实现波动率
- Barndorff-Nielsen & Shephard (2002): 二次幂变差
- Hansen & Lunde (2006): 已实现核估计量
- 最优采样频率：A股通常5分钟，避免微观结构噪声

### 1.2 HAR-RV模型
- Corsi (2009): RV_t = c + β_d*RV_d + β_w*RV_w + β_m*RV_m
- 捕获波动率的长记忆性(long memory)
- A股HAR-RV预测力R²通常在0.3-0.5
- 加入跳跃成分(HAR-RV-J)可提升预测精度

