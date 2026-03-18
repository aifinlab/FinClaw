# 输出结构定义

建议脚本输出以下结构：

```json
{
  "skill_name": "bank-t123-corporate-finance-creditdue-diligence-review-assistant",
  "company_name": "企业名称",
  "review_stage": "审查复核",
  "hard_stoppers": [],
  "key_review_points": [],
  "general_watch_items": [],
  "evidence_gaps": [],
  "inconsistencies": [],
  "supplement_requests": [],
  "review_questions": [],
  "risk_mitigants": [],
  "initial_recommendation": "审慎推进",
  "next_steps": [],
  "summary": "自然语言摘要"
}
```

## 重点字段说明

- `hard_stoppers`：当前若不补证据或不解释清楚，就不宜继续推进的阻断项
- `key_review_points`：审查岗应优先盯住的核心问题
- `general_watch_items`：一般关注事项
- `evidence_gaps`：材料和证据缺口
- `inconsistencies`：不同材料、口径或数据之间的不一致
- `supplement_requests`：建议补收的材料和说明
- `review_questions`：建议对客户经理或企业继续追问的问题
- `risk_mitigants`：可能的风险缓释方向
- `initial_recommendation`：仅为初步审查建议，不替代最终审批结论
