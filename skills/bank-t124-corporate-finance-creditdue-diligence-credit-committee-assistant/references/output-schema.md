# 输出结构定义

建议脚本输出以下结构：

```json
{
  "skill_name": "bank-t124-corporate-finance-creditdue-diligence-credit-committee-assistant",
  "company_name": "企业名称",
  "committee_stage": "上会前准备",
  "hard_stoppers": [],
  "supporting_points": [],
  "opposing_points": [],
  "key_disputes": [],
  "vote_items": [],
  "evidence_gaps": [],
  "committee_questions": [],
  "conditional_approval_terms": [],
  "initial_committee_suggestion": "审慎上会",
  "next_steps": [],
  "summary": "自然语言摘要"
}
```

## 重点字段说明

- `hard_stoppers`：若不先解决，不宜上会拍板的阻断项
- `supporting_points`：支持继续推进的核心理由及证据
- `opposing_points`：反对或审慎推进的核心理由
- `key_disputes`：会上应重点讨论的争议点
- `vote_items`：需要会上明确表态的拍板事项
- `evidence_gaps`：当前证据缺口
- `committee_questions`：建议会前或会上追问的问题
- `conditional_approval_terms`：如拟有条件通过，建议附加条款
- `initial_committee_suggestion`：仅为会前建议，不替代最终审批结论
