# 输入结构定义

推荐输入为 JSON 对象，适合供应链尽调和链路核验。

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
- `application.amount_mn`
- `application.purpose`
- `operations.core_enterprise`
- `operations.trade_chain`
- `operations.receivable_verifiability`
- `materials`

## 最低可用输入

- 申请主体名称
- 核心企业
- 贸易链路说明
- 融资金额
- 核心贸易和应收材料
