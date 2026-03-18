# 输入结构定义

推荐输入为 JSON 对象，适合房地产项目或地产主体授信判断。

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
- `operations.project_list`
- `operations.sell_through_rate`
- `financials.restricted_cash_mn`
- `financials.cash_mn`
- `external_risks.policy_pressure`

## 最低可用输入

- 企业名称
- 项目清单
- 申请金额
- 受限资金或可支配现金
- 项目销售去化信息
