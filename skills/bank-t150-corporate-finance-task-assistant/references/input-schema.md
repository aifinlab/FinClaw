# 输入结构定义

```json
{
  "company": { "name": "企业名称" },
  "verification": {
    "time_window": "近12个月",
    "contracts": [
      {
        "contract_id": "HT-2026-001",
        "counterparty": "上海某某贸易有限公司",
        "amount": 800000.0,
        "payment_terms": "验收合格后90天付款；逾期按日万分之五计收违约金。",
        "invoice_terms": "先票后款，增值税专票。",
        "acceptance_terms": "到货后15天内完成验收，逾期视为验收通过。",
        "other_terms": "发生争议提交对方所在地法院。"
      }
    ]
  }
}
```

## 最低可用输入

- `company.name`
- `verification.time_window`
- `verification.contracts`

