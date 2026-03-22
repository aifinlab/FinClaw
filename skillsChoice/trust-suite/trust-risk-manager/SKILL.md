# trust-risk-manager

## 描述
信托风险全流程管理工具，覆盖信用风险、市场风险、流动性风险、操作风险四大维度，提供实时监控、预警提示和风险处置建议。

## 功能
- 信用风险评估（融资主体、担保措施、偿债能力）
- 市场风险监控（利率、汇率、商品价格敏感性）
- 流动性风险分析（期限错配、赎回压力、变现能力）
- 操作风险检查（流程合规、系统安全）
- 风险预警指标（VaR、CVaR、压力测试）
- 风险限额管理（集中度、久期、杠杆）
- 风险报告生成

## 使用场景
- 风控部门日常监控
- 投后管理风险排查
- 新产品风险评审
- 监管报送数据准备
- 风险预警处置

## 输入输出

### 输入
```json
{
  "portfolio_id": "",
  "risk_type": "all|credit|market|liquidity|operation",
  "assets": [
    {
      "asset_id": "",
      "asset_type": "非标债权|股票|债券|基金",
      "exposure": 1000000,
      "credit_rating": "AA+",
      "maturity_date": "2027-03-20",
      "counterparty": ""
    }
  ],
  "confidence_level": 0.95,
  "time_horizon": 1,
  "stress_scenarios": ["利率上升100bp", "股市下跌20%", "信用利差扩大200bp"]
}
```

### 输出
```json
{
  "status": "success",
  "data": {
    "overall_risk_score": 65,
    "risk_level": "中等",
    "var_95": 1250000,
    "cvar_95": 1800000,
    "credit_risk": {
      "score": 70,
      "exposure_by_rating": {"AAA": 30, "AA+": 40, "AA": 30},
      "concentration_risk": 0.35
    },
    "market_risk": {
      "score": 60,
      "duration": 2.5,
      "convexity": 8.2,
      "beta": 0.85
    },
    "liquidity_risk": {
      "score": 65,
      "liquidity_ratio": 1.2,
      "maturity_mismatch": 0.15
    },
    "stress_test": {
      "利率上升100bp": {"portfolio_value_change": -3.2},
      "股市下跌20%": {"portfolio_value_change": -8.5}
    },
    "early_warnings": [
      {"level": "yellow", "indicator": "单一主体集中度超限", "threshold": "15%", "current": "18%"}
    ]
  }
}
```

## 运行方式

```bash
# 全面风险评估
python scripts/main.py --portfolio-id "PTF001" --risk-type all

# 信用风险专项
python scripts/main.py --risk-type credit --assets data/assets.json

# 压力测试
python scripts/main.py --stress-test --scenarios data/scenarios.json

# 风险预警监控
python scripts/main.py --monitor --watchlist data/watchlist.json
```

## 依赖
- numpy>=1.23.0
- pandas>=1.5.0
- scipy>=1.9.0
- statsmodels>=0.13.0
- arch>=5.3.0

## 风险指标说明

| 指标 | 说明 | 阈值 |
|---|---|---|
| VaR (95%) | 95%置信度下的最大损失 | <5%总资产 |
| CVaR | 条件VaR，尾部风险 | <8%总资产 |
| 久期 | 利率敏感度 | <3年 |
| 集中度 | 单一主体占比 | <15% |
| 流动性比率 | 流动资产/总资产 | >1.0 |

## 免责声明
本工具提供的风险评估结果仅供参考，不构成风险处置建议。实际风险管理需结合定性分析和专业判断。

## 许可证
MIT License
