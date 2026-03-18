# 输出结构建议

```json
{
  "customer_id": "客户编号",
  "warning_level": "低/中/高/紧急",
  "overall_score": 0,
  "signals": [
    {
      "dimension": "资产/交易/产品/关系/竞品/服务",
      "signal": "信号名称",
      "severity": "低/中/高",
      "evidence": "证据说明"
    }
  ],
  "industry_support": {
    "available": true,
    "support_level": "强/中/弱",
    "note": "行业数据支持说明"
  },
  "main_reasons": ["主要原因"],
  "to_be_verified": ["待核验事项"],
  "retention_actions": ["经营建议"],
  "next_observation_points": ["后续观察指标"]
}
```
