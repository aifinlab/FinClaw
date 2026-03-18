# 输入结构定义

推荐输入为 JSON 对象，适合制造业客户授信判断。

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
- `application.product_type`
- `application.purpose`
- `operations.capacity_utilization`
- `operations.order_backlog_mn`
- `operations.raw_material_volatility`
- `operations.main_products`
- `materials`

## 最低可用输入

- 企业名称
- 授信金额
- 在手订单
- 产能利用率
- 用途和还款来源
