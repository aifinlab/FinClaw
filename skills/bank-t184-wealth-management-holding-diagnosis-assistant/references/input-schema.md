# 输入结构（建议）

```json
{
  "client_profile": {
    "name": "张三",
    "risk_level": "稳健",
    "investment_horizon_months": 24,
    "liquidity_need": "中",
    "goals": ["稳健增值", "子女教育"],
    "constraints": ["不投高波动品类"],
    "preferred_currency": "CNY"
  },
  "diagnosis_scope": {
    "as_of_date": "2026-03-10",
    "performance_window": "近12个月",
    "currency": "CNY"
  },
  "holdings": [
    {
      "asset_name": "稳健固收+产品A",
      "asset_class": "固收",
      "product_type": "理财",
      "issuer": "XX理财子",
      "market_value": 520000,
      "cost_value": 500000,
      "return_3m": 0.012,
      "return_12m": 0.035,
      "risk_level": "稳健",
      "liquidity": "中",
      "min_holding_months": 6
    }
  ],
  "market_context": {
    "rates_trend": "利率下行",
    "equity_volatility": "偏高",
    "sector_events": ["房地产信用分化"],
    "policy_notes": ["存量房贷利率调整"],
    "advisor_view": "今年债券有一定票息支撑"
  },
  "constraints": {
    "max_single_product_pct": 25,
    "max_single_issuer_pct": 35,
    "max_equity_pct": 60
  }
}
```

字段说明：
- `client_profile`：客户画像与约束
- `diagnosis_scope`：诊断口径（时间区间/币种/估值日期）
- `holdings`：持仓明细，至少包含资产类别、市值与风险等级
- `market_context`：市场/行业/政策背景信息（可选）
- `constraints`：集中度或结构上限（可选）
