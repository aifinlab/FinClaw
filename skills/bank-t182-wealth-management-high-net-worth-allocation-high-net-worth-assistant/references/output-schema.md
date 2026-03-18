# 输出结构（建议）

```json
{
  "skill_name": "bank-t182-wealth-management-high-net-worth-allocation-high-net-worth-assistant",
  "title": "高净值客户资产配置",
  "mode": "hnw_allocation",
  "profile_snapshot": {
    "name": "客户A",
    "risk_level": "中高",
    "investment_horizon_months": 60,
    "liquidity_need": "中",
    "aum_total": "5000万",
    "currency_mix": "CNY 70%, USD 30%",
    "goals": ["稳健增值", "教育金"],
    "family_goals": ["家族传承", "养老保障"]
  },
  "summary": "已生成高净值分层配置建议，可结合家族目标与产品池落地。",
  "gaps": ["缺少家族目标或长期规划信息。"],
  "allocation_target": {
    "liquidity": 12,
    "core": 42,
    "growth": 26,
    "alternative": 15,
    "protection": 5
  },
  "allocation_current": {
    "liquidity": 5,
    "core": 48,
    "growth": 32,
    "alternative": 15
  },
  "allocation_logic": ["期限偏短：提高流动性与核心仓占比。"],
  "allocation_layers": {
    "liquidity": "流动性仓说明",
    "core": "核心稳健仓说明"
  },
  "goal_mapping": [
    {"goal": "教育金", "bucket": "liquidity"},
    {"goal": "家族传承", "bucket": "protection"}
  ],
  "rebalance_actions": [
    "liquidity 当前5% → 目标12%，建议增加7个百分点。"
  ],
  "product_shortlist": [
    {
      "product_id": "A001",
      "name": "稳健固收组合",
      "status": "适配",
      "score": 78.5
    }
  ],
  "not_suitable_products": [],
  "risk_notes": ["适配结论仅基于当前披露信息，不构成收益承诺或投资建议。"],
  "communication_points": ["强调高净值客户资产的流动性分层与家族目标匹配。"],
  "follow_up": ["补齐关键资料后再锁定最终方案。"]
}
```
