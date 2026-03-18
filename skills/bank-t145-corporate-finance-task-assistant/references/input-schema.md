# 输入结构定义

推荐输入为 JSON 对象，用于生成对公客户画像一页纸。

```json
{
  "company": {
    "name": "企业名称",
    "industry": "行业（可选）",
    "region": "区域（可选）"
  },
  "portrait": {
    "time_window": "近12个月/2025Q4等口径说明"
  },
  "business": {
    "model_summary": "一句话商业模式（怎么赚钱、客户是谁、回款怎么回）"
  },
  "financials": {
    "revenue_mn": 1200.0,
    "profit_mn": 35.0,
    "operating_cf_mn": -20.0,
    "debt_mn": 500.0,
    "revenue_growth": "上升/下降/稳定（可选）"
  },
  "exposures": {
    "relationship_with_bank": "我行合作情况（可选）",
    "customer_concentration_top1": 0.55,
    "related_party_complexity": true
  },
  "external_risks": {
    "major_negative_news": "负面新闻摘要（可选）",
    "legal_cases": 3,
    "tax_arrears": 0
  }
}
```

## 最低可用输入

- `company.name`
- `portrait.time_window`
- `business.model_summary`

