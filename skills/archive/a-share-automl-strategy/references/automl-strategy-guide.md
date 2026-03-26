# AutoML策略/自动化建模助手参考指南

## 一、AutoML量化

### 1.1 AutoML框架
- AutoGluon：Amazon开源，表格数据AutoML
- FLAML：Microsoft开源，快速轻量AutoML
- H2O AutoML：企业级AutoML平台

### 1.2 量化AutoML注意事项
- 必须使用时序交叉验证，不能随机分割
- 搜索空间需包含金融领域常用模型
- 评估指标用IC/Sharpe而非通用ML指标
- AutoML是起点不是终点，仍需人工审查

