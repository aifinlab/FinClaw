# 输出结构定义

建议脚本输出以下结构：

```json
{
  "skill_name": "bank-t122-corporate-finance-creditdue-diligence-rm-assistant",
  "company_name": "企业名称",
  "due_diligence_stage": "客户经理尽调",
  "data_gaps": [],
  "supplement_list": [],
  "management_interview_questions": [],
  "site_visit_focus": [],
  "risk_hypotheses": [],
  "internal_alerts": [],
  "next_steps": [],
  "summary": "自然语言摘要"
}
```

## 重点字段说明

- `data_gaps`：当前尽调仍然缺失的关键信息
- `supplement_list`：建议客户经理优先向客户补收的材料
- `management_interview_questions`：建议当面或电话追问的问题
- `site_visit_focus`：去现场时最应该核验的点
- `risk_hypotheses`：当前最值得验证的风险假设
- `internal_alerts`：需要提前向内部审查或团队打招呼的问题
- `next_steps`：下一步推进顺序
