# 输入结构（建议）

建议以 JSON 形式提供：

```json
{
  "client_profile": {
    "name": "张三",
    "risk_level": "稳健",
    "investment_horizon_months": 12,
    "liquidity_need": "中",
    "goals": ["稳健增值", "现金流"],
    "constraints": ["最大回撤不超过8%"],
    "preferred_currency": "CNY"
  },
  "current_portfolio": [
    {
      "asset_class": "fixed_income",
      "product_name": "某银行理财A",
      "market_value": 500000,
      "min_holding_months": 6
    }
  ],
  "product_pool": [
    {
      "product_id": "P001",
      "name": "稳健理财1号",
      "asset_class": "fixed_income",
      "risk_level": 2,
      "min_holding_months": 6,
      "liquidity": "T+1",
      "expected_return_range": "2.8%-3.6%",
      "tags": ["稳健", "现金流"]
    }
  ],
  "preferences": {
    "avoid_products": ["高波动权益"],
    "preferred_asset_classes": ["fixed_income", "cash"]
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
- `current_portfolio`
- `preferences`
- `market_view`
