# 输入结构（建议）

```json
{
  "client_profile": {
    "name": "客户A",
    "age": 45,
    "risk_level": "中高",
    "investment_horizon_months": 60,
    "liquidity_need": "中",
    "aum_total": "5000万",
    "goals": ["稳健增值", "教育金"],
    "family_goals": ["家族传承", "养老保障"],
    "constraints": ["单一资产不超过25%", "保留一年现金流"],
    "preferred_currency": "CNY",
    "currency_mix": "CNY 70%, USD 30%",
    "family_context": "家庭三代同堂，关注教育与养老"
  },
  "current_portfolio": [
    {
      "asset_class": "fixed_income",
      "product_name": "固收组合",
      "market_value": 20000000
    },
    {
      "asset_class": "equity",
      "product_name": "权益组合",
      "market_value": 15000000
    },
    {
      "asset_class": "alternative",
      "product_name": "不动产类产品",
      "market_value": 8000000
    },
    {
      "asset_class": "cash",
      "product_name": "活期/货基",
      "market_value": 2000000
    }
  ],
  "product_pool": [
    {
      "product_id": "A001",
      "name": "稳健固收组合",
      "asset_class": "fixed_income",
      "risk_level": 2,
      "min_holding_months": 6,
      "liquidity": "T+1",
      "expected_return_range": "2.8%-3.6%",
      "tags": ["稳健", "现金流"]
    }
  ],
  "market_view": {
    "equity_outlook": "中性",
    "fixed_income_outlook": "稳健",
    "alternative_outlook": "谨慎"
  }
}
```

## 必填字段
- `client_profile.risk_level`
- `client_profile.investment_horizon_months`
- `client_profile.liquidity_need`
- `client_profile.goals`
- `client_profile.aum_total`
- `current_portfolio`
- `product_pool`

## 建议字段
- `client_profile.family_goals`
- `client_profile.currency_mix`
- `client_profile.constraints`
- `market_view`
