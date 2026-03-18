# 定投建议输入 schema（示例）

以下为推荐的输入字段结构（JSON），字段可裁剪，但应保持关键字段：

```json
{
  "client_profile": {
    "name": "客户A",
    "risk_level": "平衡",
    "investment_horizon_months": 36,
    "liquidity_need": "中",
    "max_drawdown_tolerance": "中",
    "goals": ["子女教育", "长期增值"],
    "constraints": ["不投单一行业基金"]
  },
  "sip_plan": {
    "monthly_amount": 3000,
    "frequency": "每月",
    "start_date": "2026-04",
    "duration_months": 36,
    "target_amount": 120000
  },
  "product_pool": [
    {
      "product_id": "F001",
      "name": "稳健债基A",
      "asset_class": "固收",
      "risk_level": "稳健",
      "min_holding_months": 6,
      "fee_rate": 0.8,
      "volatility_level": "低",
      "tags": ["稳健", "现金流"]
    },
    {
      "product_id": "F002",
      "name": "均衡混合B",
      "asset_class": "混合",
      "risk_level": "平衡",
      "min_holding_months": 12,
      "fee_rate": 1.2,
      "volatility_level": "中",
      "tags": ["长期增值"]
    }
  ],
  "market_view": {
    "notes": ["短期波动上升，强调长期纪律"]
  },
  "constraints": {
    "forbidden_categories": ["单一行业基金"],
    "channel_limit": "仅代销产品"
  }
}
```

必填建议字段：
- `client_profile.risk_level`
- `client_profile.investment_horizon_months`
- `client_profile.liquidity_need`
- `client_profile.goals`
- `sip_plan.monthly_amount` 或 `sip_plan.target_amount`
- `sip_plan.duration_months`
- `product_pool`
