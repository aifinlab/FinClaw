# 输入结构（t141 经营波动监测）

```json
{
  "company": {
    "name": "示例公司",
    "uscc": "可选",
    "industry": "可选"
  },
  "monitoring": {
    "time_window": "2025Q3~2026Q1",
    "kpi_definitions": {
      "period_type": "Q",
      "basis": "合并口径",
      "change_basis": "环比",
      "notes": "是否剔除一次性等"
    },
    "baseline": {
      "peer_group": "同业/同地区(可选)",
      "industry_event": "行业共振/政策冲击(可选)"
    },
    "alerts": [
      "系统告警：经营现金流转负",
      "人工观察：大客户回款延迟"
    ],
    "kpis": [
      {
        "period": "2025Q4",
        "revenue_mn": 1200,
        "net_profit_mn": 60,
        "operating_cashflow_mn": 30
      },
      {
        "period": "2026Q1",
        "revenue_mn": 780,
        "net_profit_mn": 18,
        "operating_cashflow_mn": -25
      }
    ]
  }
}
```

说明：
- KPI 建议最少包含：`revenue_mn`、`net_profit_mn`、`operating_cashflow_mn`（单位：百万元）。
- 若你有更细指标（应收/存货/短债/利息覆盖等），可继续扩展字段，文档里注明口径即可。

