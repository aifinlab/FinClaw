# 输入结构定义

```json
{
  "company": { "name": "企业名称" },
  "verification": {
    "time_window": "近6个月/2025Q4等",
    "transactions": [
      {
        "date": "2026-01-05",
        "amount": 120000.0,
        "direction": "in",
        "counterparty": "上海某某贸易有限公司",
        "summary": "货款回款",
        "account_no": "6222****",
        "balance": 980000.0
      }
    ]
  }
}
```

## 最低可用输入

- `company.name`
- `verification.time_window`
- `verification.transactions`

