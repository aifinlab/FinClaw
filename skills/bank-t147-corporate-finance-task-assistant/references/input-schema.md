# 输入结构定义

推荐输入为 JSON 对象，用于生成产品组合方案（主方案+备选）。

```json
{
  "company": {
    "name": "企业名称",
    "industry": "行业（可选）"
  },
  "needs": {
    "goal": "核心目标（例如：贸易融资+结算沉淀）",
    "constraints": {
      "tenor": "6-12个月",
      "credit_quota_limit_mn": 80,
      "must_have": ["保函"],
      "avoid": ["高波动理财"]
    }
  },
  "product_catalog": [
    {
      "name": "流动资金贷款",
      "tags": ["financing"],
      "notes": "适用条件与要点"
    }
  ]
}
```

## 最低可用输入

- `company.name`
- `needs.goal`
- `needs.constraints`

