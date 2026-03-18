# 输出结构（t135 现金流压力诊断包）

脚本输出为一个 JSON 对象（也可渲染为 Markdown），字段如下：

```json
{
  "skill_name": "bank-t135-corporate-finance-task-assistant",
  "title": "企业现金流压力诊断包",
  "stage": "现金流压力诊断",
  "focus": ["..."],
  "recommendation": "补强证据后推进 | 审慎推进并设置条件 | 建议暂缓并升级处置 | 可进入下一环节",
  "summary": "一句话+两句话的结构化摘要",
  "gaps": ["关键信息缺口1", "关键信息缺口2"],
  "red_flags": ["重点风险/异常信号1", "重点风险/异常信号2"],
  "verification_points": ["重点核验要点..."],
  "supplement_list": ["补件清单..."],
  "questions": ["沟通与访谈问题..."],
  "next_steps": ["下一步动作..."]
}
```

使用建议：

- `gaps`：用于“缺什么材料/字段才敢下判断”
- `red_flags`：用于“优先级最高的风险点”
- `verification_points`：用于现场核验/穿透核验
- `questions`：用于访谈提纲（管理层/财务/销售/采购）
- `next_steps`：用于形成贷后动作、审查要点或客户沟通计划

