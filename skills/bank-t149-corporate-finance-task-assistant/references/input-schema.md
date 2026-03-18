# 输入结构定义

```json
{
  "company": { "name": "企业名称" },
  "verification": {
    "time_window": "近12个月",
    "invoices": [
      {
        "invoice_no": "044001234567",
        "date": "2026-01-12",
        "seller": "深圳某某科技有限公司",
        "buyer": "上海某某贸易有限公司",
        "amount": 100000.0,
        "tax_rate": 13,
        "tax_amount": 13000.0,
        "total_amount": 113000.0,
        "status": "正常",
        "item": "设备配件"
      }
    ]
  }
}
```

## 最低可用输入

- `company.name`
- `verification.time_window`
- `verification.invoices`

