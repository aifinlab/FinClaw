# 输出结构定义

脚本支持 Markdown/JSON 两种输出，JSON 结构如下：

```json
{
  "skill_name": "bank-t152-retail-finance-customer-operation-assistant",
  "title": "场景标题",
  "stage": "运营编排",
  "recommendation": "建议结论",
  "summary": "结构化摘要",
  "priority_list": [
    {
      "customer_id": "C001",
      "name": "客户姓名",
      "score": 82.5,
      "segment": "客群标签"
    }
  ],
  "action_list": ["动作建议"],
  "gaps": ["信息缺口"],
  "red_flags": ["风险提示"],
  "supplement_list": ["补充清单"],
  "questions": ["沟通问题"],
  "next_steps": ["下一步动作"]
}
```
