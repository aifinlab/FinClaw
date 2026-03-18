# 输出结构（t141 经营波动监测）

```json
{
  "scenario_id": "t141",
  "time_window": "最近2期/3期",
  "risk_level": "红/橙/黄/绿",
  "priority": "P0-P3",
  "summary": "一句话结论 + 边界",
  "kpi_snapshot": {
    "period": "最近一期",
    "revenue_mn": 780,
    "net_profit_mn": 18,
    "operating_cashflow_mn": -25,
    "revenue_change": "-35.0%",
    "net_profit_change": "-70.0%",
    "operating_cashflow_change": "待补"
  },
  "alerts": ["..."],
  "anomalies": ["..."],
  "drivers_to_verify": ["..."],
  "gaps": ["..."],
  "actions": ["..."],
  "customer_comms_script": ["..."]
}
```

