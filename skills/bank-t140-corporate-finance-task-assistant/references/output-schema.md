# 输出结构（t140 诉讼/处罚扫描）

脚本输出为一个 JSON 对象（`--format json`）或 Markdown 简报（`--format markdown`）。

核心字段（JSON）：

```json
{
  "skill_name": "bank-t140-corporate-finance-task-assistant",
  "title": "企业诉讼/处罚扫描简报",
  "stage": "风险监测",
  "audience": "对公客户经理/审查/贷后/风险",
  "focus": ["..."],
  "company": {"name": "...", "uscc": "..."},
  "scenario_id": "t140",
  "time_window": "近期",
  "risk_level": "红/橙/黄/绿",
  "priority": "P0-P3",
  "summary": "一句话结论 + 边界声明",
  "highlights": ["..."],
  "key_events": [
    {
      "date": "...",
      "event_type": "...",
      "role": "...",
      "status": "...",
      "counterparty": "...",
      "amount_mn": 1.0,
      "risk_score": 4.5,
      "severity": "重大/高/中/一般"
    }
  ],
  "event_briefs": ["..."],
  "gaps": ["..."],
  "verification_points": ["..."],
  "actions": ["..."],
  "escalation_triggers": ["..."]
}
```

注意：
- `risk_level/priority` 为“监测分级”，不等价于法律定性或审批结论。
- `key_events` 为脚本从输入事件中挑选的高优先级节选（默认最多 8 条）。

