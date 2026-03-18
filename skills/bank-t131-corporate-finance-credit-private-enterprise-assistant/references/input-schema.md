# 输入结构定义

推荐输入为 JSON 对象，适合民企授信判断。

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

- `company.name`
- `company.actual_controller`
- `application.amount_mn`
- `application.purpose`
- `external_risks.pledged_shares_ratio`
- `external_risks.external_guarantee_pressure`
- `materials`

## 最低可用输入

- 企业名称
- 实控人
- 申请金额
- 第一还款来源
- 股权质押或担保信息
