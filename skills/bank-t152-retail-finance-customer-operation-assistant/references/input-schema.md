# 输入结构定义

推荐输入为 JSON 对象：

`json
{
  "batch_id": "2026W11-t152",
  "time_window": "近30天",
  "goal": "AUM提升/新客转化/唤醒挽回/高净值识别",
  "customers": [
    {
      "customer_id": "C001",
      "name": "客户姓名",
      "segment": "客群标签",
      "mobile": "138****8888",
      "consent_marketing": true,
      "aum": 1200000,
      "deposit": 300000,
      "product_count": 2,
      "last_active_days": 18,
      "risk_flags": ["无"],
      "app_last_active_days": 9,
      "campaign_clicks_30d": 2,
      "txn_count_30d": 5,
      "days_since_onboarding": 14,
      "has_bind_card": true,
      "has_first_txn": false,
      "has_salary_inflow": true,
      "silence_days": 65,
      "aum_drop_ratio": 0.32,
      "recent_complaint": false,
      "annual_income": 860000,
      "net_inflow_90d": 260000,
      "complex_need_count": 2,
      "salary_customer": true
    }
  ]
}
`

## 最低可用输入

- atch_id
- 	ime_window
- customers（至少 1 条记录）
