# 期权Greeks/风险敞口分析助手参考指南

## 一、Greeks基础

### 1.1 五大Greeks
- Delta(Δ)：方向风险，Call正/Put负
- Gamma(Γ)：凸性风险，买方正/卖方负
- Theta(Θ)：时间风险，买方负/卖方正
- Vega(ν)：波动率风险，买方正/卖方负
- Rho(ρ)：利率风险，通常影响较小

### 1.2 A股Greeks特点
- A股期权以ETF期权为主，Greeks计算标准
- T+1标的限制了Delta对冲的灵活性
- 涨跌停制度影响极端情况下的Greeks估计
- 做市商Greeks管理：需要实时监控组合敞口

