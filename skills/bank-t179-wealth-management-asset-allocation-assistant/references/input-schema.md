# 输入结构（建议）

```json
{
  "client_profile": {
    "name": "客户A",
    "risk_level": "稳健",
    "investment_horizon_months": 24,
    "liquidity_need": "中",
    "goals": ["稳健增值"],
    "constraints": ["单一资产不超过30%"]
  },
  "current_portfolio": [
    {
      "asset_class": "fixed_income",
      "product_name": "固收组合",
      "market_value": 600000
    },
    {
      "asset_class": "equity",
      "product_name": "权益组合",
      "market_value": 300000
    }
  ],
  "product_pool": [
    {
      "product_id": "A001",
      "name": "稳健理财1号",
      "asset_class": "fixed_income",
      "risk_level": 2,
      "min_holding_months": 6,
      "liquidity": "T+1",
      "expected_return_range": "2.8%-3.6%",
      "tags": ["稳健"]
    }
  ]
}
```

## 必填字段
- `client_profile.risk_level`
- `client_profile.investment_horizon_months`
- `client_profile.liquidity_need`
- `client_profile.goals`
- `current_portfolio`
- `product_pool`

## 可选字段
- `preferences`
- `market_view`
