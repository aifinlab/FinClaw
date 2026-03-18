# 输出结构（摘要）

```json
{
  "skill_name": "bank-t176-wealth-management-product-suitability-rm-assistant",
  "title": "理财产品适配（理财经理版）",
  "mode": "suitability",
  "profile_snapshot": {
    "name": "张三",
    "risk_level": "稳健",
    "investment_horizon_months": 12,
    "liquidity_need": "中"
  },
  "summary": "已基于风险等级、期限与流动性完成产品适配初筛。",
  "suitable_products": [
    {
      "product_id": "P001",
      "name": "稳健理财1号",
      "asset_class": "fixed_income",
      "status": "适配",
      "score": 86.0,
      "reasons": []
    }
  ],
  "not_suitable_products": [
    {
      "product_id": "P009",
      "name": "高波动权益产品",
      "status": "不适配",
      "reasons": ["产品风险等级高于客户风险承受能力。"]
    }
  ],
  "gaps": ["缺少投资期限或持有周期。"],
  "risk_notes": [],
  "communication_points": [],
  "follow_up": []
}
```
