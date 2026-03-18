# 输入结构（t140 诉讼/处罚扫描）

推荐使用 JSON 输入，最小可行字段如下（字段可以缺，但缺失会进入 `gaps`）：

```json
{
  "company": {
    "name": "示例公司",
    "uscc": "统一社会信用代码(建议)",
    "registration_no": "注册号(可选)",
    "industry": "行业(可选)"
  },
  "monitoring": {
    "time_window": "2026-01-01~2026-03-15",
    "sources": [
      {"name": "裁判文书网/第三方聚合", "update_freq": "T+1", "notes": "口径说明"}
    ],
    "baseline": {
      "window": "过去12个月",
      "new_cases_count": 3
    }
  },
  "events": [
    {
      "date": "2026-03-01",
      "event_type": "行政处罚",
      "role": "被处罚人",
      "status": "处罚决定",
      "authority": "监管机构/法院/执法机关(可选)",
      "counterparty": "对手方/申请人/原告/监管机构",
      "amount_mn": 2.5,
      "amount_text": "罚款250万元(可选)",
      "case_no": "案号/文号(可选)",
      "summary": "事件简述(可选)",
      "last_update": "2026-03-05(可选)"
    }
  ],
  "exposures": {
    "credit_exposure_mn": 80,
    "guarantee_exposure_mn": 20
  }
}
```

字段说明与建议：
- `company.uscc/registration_no`：用于防止同名误匹配，强烈建议至少提供一个。
- `events[].role/status`：用于分级（被执行/失信/处罚决定通常优先级更高）。
- `events[].amount_mn`：单位建议统一为“百万元”；若只有文本可放 `amount_text`。

