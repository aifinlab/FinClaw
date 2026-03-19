# Transformer量化/注意力因子助手参考指南

## 一、Transformer量化

### 1.1 金融Transformer
- Ding et al. (2020): Transformer用于股票排序
- Yun et al. (2021): 时空Transformer捕获截面+时序
- A股实证：Transformer在因子组合上优于线性模型

### 1.2 注意力机制价值
- 注意力权重提供模型可解释性
- 动态权重：不同市场状态下关注不同因子
- 跨股票注意力揭示隐含的行业/概念关联
- 计算成本高：需要GPU，推理延迟需优化

