# 定投建议输出 schema（示例）

脚本输出包含以下核心结构：

```json
{
  "title": "定投建议输出",
  "profile_snapshot": {
    "name": "客户A",
    "risk_level": "平衡",
    "investment_horizon_months": 36,
    "liquidity_need": "中",
    "goals": ["子女教育"],
    "max_drawdown_tolerance": "中"
  },
  "sip_structure": {
    "monthly_amount": 3000,
    "duration_months": 36,
    "target_amount": 120000,
    "frequency": "每月",
    "start_date": "2026-04",
    "step_up_suggestion": "建议每12个月根据收入提升10%-15%逐步加码"
  },
  "plan_options": {
    "risk_bucket": "balanced",
    "target_allocation": {
      "fixed_income": 40,
      "equity": 45,
      "cash": 15
    },
    "primary_plan": [
      {"asset_class": "fixed_income", "weight": 40, "product": "稳健债基A", "score": 78.5}
    ],
    "backup_plan": []
  },
  "suitable_products": [],
  "not_suitable_products": [],
  "gaps": [],
  "communication_points": [],
  "risk_notes": [],
  "follow_up": []
}
```

说明：
- `primary_plan` / `backup_plan` 可能为空，需配合 `gaps` 输出提示
- `gaps` 用于标注缺失信息，不得忽略
- `risk_notes` 与 `communication_points` 为对客沟通与留痕重点
