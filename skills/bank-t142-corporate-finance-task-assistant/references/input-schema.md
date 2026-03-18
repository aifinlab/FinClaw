# 输入结构（t142 贷后回访纪要）

```json
{
  "company": {"name": "示例公司", "uscc": "可选"},
  "visit": {
    "visit_date": "2026-03-10",
    "purpose": "贷后回访/用途核验/押品检查",
    "attendees": ["客户经理A", "财务负责人B"],
    "information_sources": ["现场观察", "客户口述", "台账", "流水(节选)"],
    "key_updates": [
      "订单较上季下降，交付周期拉长（口述，待核验）",
      "新增核心客户C，已开始回款（材料待补）"
    ],
    "risk_observations": [
      "应收账龄拉长，回款延迟",
      "受限资金占比上升（待核验）"
    ],
    "loan_use_check": "资金用途核验结论（四流合一/替代证据）",
    "repayment_source_update": "还款来源更新与备用安排",
    "covenant_compliance": "承诺/条款遵循情况（若不确定写待确认）",
    "action_items": [
      {"item": "补充合同/发票/验收资料", "owner": "客户经理A", "due_date": "2026-03-15"},
      {"item": "提供应收账龄明细与前10客户回款", "owner": "财务负责人B", "due_date": "2026-03-18"}
    ]
  }
}
```

最小可行输入：
- `company.name`
- `visit.visit_date`
- `visit.purpose`

