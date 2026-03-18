# 输出字段规范

```json
{
  "skill_name": "enterprise-financial-health-diagnosis",
  "enterprise_name": "企业名称",
  "reporting_period": "报表期间",
  "scope": "合并/单体",
  "currency": "币种",
  "diagnosis_type": "综合诊断/初步诊断",
  "overall_rating": "健康/基本健康/承压/高风险",
  "summary": "诊断摘要",
  "strengths": ["主要优势"],
  "risks": ["主要风险"],
  "solvency_analysis": {
    "short_term": "短期偿债判断",
    "long_term": "长期偿债判断",
    "key_metrics": {}
  },
  "profitability_analysis": {
    "trend": "盈利趋势判断",
    "quality": "盈利质量判断",
    "key_metrics": {}
  },
  "operating_analysis": {
    "receivable_turnover": "应收周转判断",
    "inventory_turnover": "存货周转判断",
    "working_capital": "营运资本判断"
  },
  "cashflow_analysis": {
    "operating_cashflow": "经营现金流判断",
    "profit_cash_match": "利润现金匹配判断",
    "financing_dependency": "融资依赖判断"
  },
  "capital_structure_analysis": {
    "leverage": "杠杆判断",
    "equity_buffer": "权益缓冲判断",
    "debt_structure": "债务结构判断"
  },
  "red_flags": [
    {
      "item": "红旗事项",
      "basis": "触发依据",
      "impact": "影响判断",
      "follow_up": "建议核验事项"
    }
  ],
  "data_gaps": ["缺失信息"],
  "follow_up_actions": ["建议动作"]
}
```
