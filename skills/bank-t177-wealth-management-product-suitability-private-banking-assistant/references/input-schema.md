# 输入结构（建议）

```json
{
  "client_profile": {
    "name": "李女士",
    "risk_level": "平衡",
    "investment_horizon_months": 36,
    "liquidity_need": "中",
    "goals": ["家族财富稳健增值", "教育金"],
    "constraints": ["单一资产不超过30%"],
    "family_context": "家庭资产多元，需兼顾长期资金与现金流安排"
  },
  "current_portfolio": [
    {
      "asset_class": "fixed_income",
      "product_name": "家族固收组合",
      "market_value": 2000000
    }
  ],
  "product_pool": [
    {
      "product_id": "PB001",
      "name": "私行稳健组合",
      "asset_class": "fixed_income",
      "risk_level": 2,
      "min_holding_months": 12,
      "liquidity": "封闭12个月",
      "expected_return_range": "3%-4%",
      "tags": ["稳健", "家族" ]
    }
  ],
  "preferences": {
    "preferred_asset_classes": ["fixed_income", "alternative"],
    "avoid_products": ["高波动权益"]
  }
}
```

## 必填字段
- `client_profile.risk_level`
- `client_profile.investment_horizon_months`
- `client_profile.liquidity_need`
- `client_profile.goals`
- `product_pool`

## 可选字段
- `family_context`
- `current_portfolio`
- `preferences`
- `market_view`
