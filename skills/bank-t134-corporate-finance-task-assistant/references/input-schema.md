# 输入结构定义

推荐输入为 JSON 对象，适合企业财报快诊。

```json
{
  "company": {},
  "financials": {},
  "materials": [],
  "external_risks": {}
}
```

## 关键字段

- `company.name`
- `financials.revenue_mn`
- `financials.net_profit_mn`
- `financials.operating_cash_flow_mn`
- `financials.gross_margin_pct`
- `financials.historical_gross_margin_pct`
- `financials.expense_ratio_pct`
- `financials.historical_expense_ratio_pct`

## 最低可用输入

- 企业名称
- 收入
- 利润
- 经营现金流
- 至少一组可比口径
