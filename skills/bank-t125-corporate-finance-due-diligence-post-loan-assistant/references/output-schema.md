# 输出结构定义

建议脚本输出以下结构：

```json
{
  "skill_name": "bank-t125-corporate-finance-due-diligence-post-loan-assistant",
  "title": "贷后尽调与监测动作包",
  "stage": "贷后尽调",
  "focus": [],
  "recommendation": "建议进入强化监测/处置",
  "summary": "自然语言摘要",
  "gaps": [],
  "red_flags": [],
  "verification_points": [],
  "supplement_list": [],
  "questions": [],
  "next_steps": []
}
```

## 重点字段说明

- `gaps`：贷后信息缺口和待补材料
- `red_flags`：已识别的异常信号和预警点
- `verification_points`：本轮贷后应优先核查的事项
- `supplement_list`：补件和补证据要求
- `questions`：对客户或经营机构需继续追问的问题
- `next_steps`：复查、监测或升级处置动作
