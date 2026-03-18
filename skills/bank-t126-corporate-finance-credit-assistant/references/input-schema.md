# 输入结构定义

推荐输入为 JSON 对象，适合小微和普惠授信的前端判断。

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

### `company`

- `name`
- `industry`
- `region`
- `actual_controller`
- `years_in_operation`

### `application`

- `amount_mn`
- `product_type`
- `purpose`
- `term_months`
- `repayment_source`

### `operations`

- `tax_invoice_match`
- `top_customers`
- `top_suppliers`
- `site_status`

### `materials`

每个材料对象建议包含：

```json
{
  "name": "近12个月纳税申报表",
  "provided": true,
  "note": "已收扫描件",
  "source": "客户经理"
}
```

## 最低可用输入

- 企业名称
- 申请金额
- 用途
- 第一还款来源
- 基础税票或流水材料
