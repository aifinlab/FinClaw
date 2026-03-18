# 输入结构定义

推荐输入为 JSON 对象，用于机会识别与风险扫描。

```json
{
  "company": { "name": "企业名称" },
  "monitoring": {
    "time_window": "近30天/近90天等",
    "signals": [
      {
        "title": "税负异常上升",
        "bucket": "risk",
        "severity": 4,
        "confidence": 0.7,
        "recency_days": 7,
        "magnitude_hint": "环比+35%"
      },
      {
        "title": "资金沉淀上升（结算机会）",
        "bucket": "opportunity",
        "severity": 2,
        "confidence": 0.8,
        "recency_days": 10,
        "suggested_products": ["现金管理", "结算归集"]
      }
    ]
  }
}
```

## 最低可用输入

- `company.name`
- `monitoring.time_window`
- `monitoring.signals`

