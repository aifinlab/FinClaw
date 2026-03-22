# trust-asset-allocation

## 描述
信托资产配置优化工具，基于现代投资组合理论(MPT)、风险平价模型和Black-Litterman框架，为信托产品提供战略/战术资产配置方案。

## 功能
- 均值-方差优化（Markowitz模型）
- 风险平价配置（Risk Parity）
- Black-Litterman贝叶斯资产配置
- 目标日期/生命周期策略
- 再平衡策略与触发条件
- 约束条件管理（投资比例、久期匹配、监管限制）
- 蒙特卡洛模拟与情景分析

## 使用场景
- 信托经理设计新产品资产配置方案
- 家族信托长期资产配置规划
- 养老信托目标日期策略
- 慈善信托保值增值配置
- FOF/MOM组合构建

## 输入输出

### 输入
```json
{
  "strategy": "mean_variance|risk_parity|black_litterman|target_date",
  "target_return": 7.5,
  "risk_tolerance": 15.0,
  "investment_horizon": 36,
  "asset_classes": [
    {"name": "现金管理类", "expected_return": 3.0, "volatility": 1.0},
    {"name": "固收类", "expected_return": 5.5, "volatility": 4.0},
    {"name": "权益类", "expected_return": 10.0, "volatility": 18.0},
    {"name": "另类投资", "expected_return": 8.0, "volatility": 12.0}
  ],
  "constraints": {
    "min_weights": {"现金管理类": 0.05, "固收类": 0.3},
    "max_weights": {"权益类": 0.4, "另类投资": 0.2},
    "max_volatility": 12.0,
    "max_drawdown": 15.0
  },
  "correlation_matrix": [...],
  "views": []  // Black-Litterman观点
}
```

### 输出
```json
{
  "status": "success",
  "data": {
    "optimal_weights": {
      "现金管理类": 0.08,
      "固收类": 0.42,
      "权益类": 0.35,
      "另类投资": 0.15
    },
    "portfolio_metrics": {
      "expected_return": 7.52,
      "volatility": 8.35,
      "sharpe_ratio": 0.72,
      "max_drawdown": 12.8,
      "calmar_ratio": 0.59
    },
    "risk_contribution": {
      "现金管理类": 0.02,
      "固收类": 0.28,
      "权益类": 0.52,
      "另类投资": 0.18
    },
    "rebalancing": {
      "frequency": "季度",
      "threshold": 0.05,
      "next_review": "2026-06-20"
    },
    "efficient_frontier": [...],
    "scenario_analysis": {...}
  }
}
```

## 运行方式

```bash
# 均值方差优化
python scripts/main.py --strategy mean_variance --target-return 7.5 --risk-tolerance 10

# 风险平价配置
python scripts/main.py --strategy risk_parity --asset-classes data/assets.json

# Black-Litterman配置
python scripts/main.py --strategy black_litterman --views data/views.json

# 目标日期策略
python scripts/main.py --strategy target_date --target-year 2045 --current-age 35
```

## 依赖
- numpy>=1.23.0
- pandas>=1.5.0
- scipy>=1.9.0
- cvxpy>=1.2.0
- matplotlib>=3.5.0
- plotly>=5.10.0
- pyportfolioopt>=1.5.0

## 算法说明

### 1. 均值-方差优化 (Markowitz)
```
minimize:  w^T * Σ * w
subject to:
  w^T * μ = target_return
  sum(w) = 1
  w >= 0 (可选)
```

### 2. 风险平价 (Risk Parity)
```
minimize:  sum((RC_i - target_RC)^2)
where RC_i = w_i * (Σ * w)_i / portfolio_volatility
```

### 3. Black-Litterman
```
E(R) = [(τΣ)^-1 + P^T * Ω^-1 * P]^-1 * [(τΣ)^-1 * Π + P^T * Ω^-1 * Q]
```

## 免责声明
本工具提供的资产配置方案仅供参考，不构成投资建议。实际投资需考虑流动性、税收、交易成本等因素。

## 许可证
MIT License
