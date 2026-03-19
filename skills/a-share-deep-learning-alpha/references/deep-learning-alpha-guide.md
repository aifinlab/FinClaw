# 深度学习Alpha信号助手参考指南

## 一、深度学习量化

### 1.1 主流架构
- Zhang et al. (2017): CNN捕获K线形态
- Feng et al. (2019): LSTM+Attention用于A股
- Xu et al. (2021): Transformer在量化中的应用

### 1.2 A股DL实践
- 数据量充足：4000+股票×250天/年
- 非线性关系丰富：散户市场模式复杂
- 挑战：regime change导致模型失效
- 建议：ensemble多个架构降低单模型风险

