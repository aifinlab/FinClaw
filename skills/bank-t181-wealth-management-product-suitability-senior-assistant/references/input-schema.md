# 输入结构（建议）

```json
{
  "client_profile": {
    "name": "王阿姨",
    "age": 68,
    "risk_level": "稳健",
    "investment_horizon_months": 12,
    "liquidity_need": "中",
    "goals": ["稳健增值", "养老补充"],
    "constraints": ["单一资产不超过30%"],
    "digital_literacy": "一般",
    "communication_preference": "面对面+纸质材料",
    "support_person": "女儿陪同"
  },
  "current_portfolio": [
    {
      "asset_class": "fixed_income",
      "product_name": "稳健理财组合",
      "market_value": 600000
    }
  ],
  "product_pool": [
    {
      "product_id": "SR001",
      "name": "稳健固收精选",
      "asset_class": "fixed_income",
      "risk_level": 2,
      "min_holding_months": 6,
      "liquidity": "半年可赎回",
      "expected_return_range": "3%-4%",
      "tags": ["稳健", "养老" ]
    }
  ],
  "preferences": {
    "preferred_asset_classes": ["fixed_income"],
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
- `client_profile.age`
- `client_profile.digital_literacy`
- `client_profile.communication_preference`
- `client_profile.support_person`
- `current_portfolio`
- `preferences`
- `market_view`
