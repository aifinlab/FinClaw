# 输出结构（建议）

```json
{
  "summary": "持仓整体稳健，但固收类占比过高导致收益弹性不足。",
  "profile_snapshot": {
    "client": "张三",
    "risk_level": "稳健",
    "investment_horizon_months": 24,
    "liquidity_need": "中"
  },
  "allocation_snapshot": {
    "by_asset_class": {
      "固收": 62,
      "权益": 18,
      "现金": 15,
      "另类": 5
    },
    "top_holdings": [
      {"asset_name": "稳健固收+产品A", "weight": 28.5}
    ]
  },
  "concentration_risks": [
    "单一产品占比 28.5%，超过阈值 25%。"
  ],
  "performance_drivers": [
    "近12个月收益主要由固收票息贡献，权益仓位贡献不足。"
  ],
  "mismatch_points": [
    "部分产品流动性低于客户需求，需确认可接受持有期。"
  ],
  "actions": [
    "适度增加权益或混合类产品提升收益弹性。",
    "降低单一产品集中度，控制在25%以内。"
  ],
  "communication_points": [
    "解释当前收益的主要来源和限制条件。"
  ],
  "data_gaps": [
    "缺少部分产品的最小持有期信息。"
  ],
  "compliance_notes": [
    "诊断为信息说明，不构成收益承诺。"
  ]
}
```
