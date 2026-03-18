# 输出结构定义

推荐脚本输出 JSON 结构如下：

```json
{
  "skill_name": "bank-t121-corporate-finance-creditpre-screen-assistant",
  "company_name": "企业名称",
  "recommendation": "可进入下一环节/有条件推进/审慎推进/不建议直接推进",
  "confidence": "高/中/低",
  "completeness": {
    "provided_count": 0,
    "required_count": 0,
    "missing_items": []
  },
  "dimension_scores": {
    "主体与治理": 0,
    "业务与行业逻辑": 0,
    "财务与现金流": 0,
    "授信用途与还款来源": 0,
    "外部风险与增信措施": 0
  },
  "hard_stop_flags": [],
  "major_watch_items": [],
  "positive_signals": [],
  "supplement_requests": [],
  "interview_questions": [],
  "next_steps": [],
  "key_metrics": {
    "资产负债率": 0.0,
    "流动比率": 0.0,
    "经营现金流/带息债务": 0.0,
    "利息保障倍数": 0.0,
    "应收/收入": 0.0
  },
  "narrative_summary": "自然语言总结"
}
```

## 字段说明

- `recommendation`：初筛建议等级
- `confidence`：对当前结论的把握程度，取决于资料完整性和证据一致性
- `completeness.missing_items`：建议补充的核心材料或字段
- `hard_stop_flags`：一旦命中就应显著下调推进意愿的红旗项
- `major_watch_items`：还不能直接否定，但必须优先核验的问题
- `positive_signals`：能够支撑项目推进的正向因素
- `supplement_requests`：补件清单
- `interview_questions`：建议对客户管理层或财务负责人追问的问题
- `next_steps`：下一步建议动作
- `narrative_summary`：适合直接贴到内部汇报或邮件中的自然语言结论

## Markdown 报告建议结构

若输出为 Markdown，建议至少包含：

1. 初筛对象概况
2. 初筛结论
3. 资料完整性
4. 关键指标概览
5. 红旗与重点关注事项
6. 补件清单
7. 访谈问题
8. 下一步建议
9. 结论边界
