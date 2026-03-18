# 输入字段参考（t166 信用卡流失预警）

建议输入为 JSON。核心字段如下：

```json
{
  "batch_id": "2026Q1-CC-CHURN-001",
  "time_window": "2026-01-01~2026-03-01",
  "policy_constraints": {
    "consent_required": true,
    "max_touch_per_week": 2
  },
  "customers": [
    {
      "customer_id": "C001",
      "name": "张三",
      "segment": "高价值",
      "aum": 500000,
      "card_spend_30d": 3200,
      "card_spend_90d": 24000,
      "active_days_30d": 2,
      "last_active_days": 45,
      "credit_limit_usage": 0.92,
      "bill_pay_delay_count": 1,
      "cash_advance_count": 1,
      "reward_redeem_drop_ratio": 0.6,
      "recent_complaint": true,
      "consent_marketing": true,
      "card_status": "active",
      "notes": "近期减少消费"
    }
  ]
}
```

字段说明：
- `batch_id`：批次标识，便于复盘
- `time_window`：观察周期
- `customers`：客户样本列表
- `card_spend_30d/90d`：近30/90天信用卡消费
- `active_days_30d`：近30天活跃天数
- `last_active_days`：距上次刷卡天数
- `credit_limit_usage`：额度使用率
- `bill_pay_delay_count`：账单延迟/逾期次数
- `reward_redeem_drop_ratio`：权益使用下降比例
- `consent_marketing`：营销授权
- `card_status`：卡片状态（active/suspended/closed）
