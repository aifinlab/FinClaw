# 输入结构定义

推荐输入为 JSON 对象，适合平台企业授信判断。

```json
{
  "company": {},
  "application": {},
  "financials": {},
  "operations": {},
  "materials": [],
  "external_risks": {}
}
```

## 关键字段

- `application.amount_mn`
- `application.purpose`
- `operations.fiscal_dependency_ratio`
- `operations.public_welfare_vs_market_revenue`
- `financials.interest_bearing_debt_mn`
- `external_risks.implicit_debt_pressure`

## 最低可用输入

- 企业名称
- 融资金额
- 财政依赖度
- 市场化收入拆分
- 债务结构概况
