# 输入结构定义

推荐输入为 JSON 对象，适合客户经理尽调场景的资料归集。

```json
{
  "company": {},
  "application": {},
  "financials": {},
  "operations": {},
  "materials": [],
  "external_risks": {},
  "site_visit": {},
  "manager_goals": {}
}
```

## 关键字段

### `company`

- `name`
- `industry`
- `region`
- `years_in_operation`
- `actual_controller`
- `shareholder_structure`

### `application`

- `product_type`
- `amount_mn`
- `term_months`
- `purpose`
- `repayment_source`
- `guarantee_mode`

### `financials`

- `revenue_mn`
- `net_profit_mn`
- `operating_cash_flow_mn`
- `total_assets_mn`
- `total_liabilities_mn`
- `interest_bearing_debt_mn`
- `accounts_receivable_mn`
- `inventory_mn`

### `operations`

- `main_products`
- `top_customers`
- `top_suppliers`
- `contract_coverage_months`
- `order_backlog_mn`
- `bank_flow_match_status`

### `materials`

每个材料对象建议包含：

```json
{
  "name": "营业执照",
  "provided": true,
  "note": "已盖章",
  "source": "客户经理已收件"
}
```

### `external_risks`

- `litigation_cases`
- `administrative_penalties`
- `major_negative_news`
- `cross_guarantee_risk`
- `dishonest_status`

### `site_visit`

- `visit_status`
- `key_observations`
- `factory_match`
- `warehouse_match`
- `management_response_quality`

### `manager_goals`

- `task_type`：本次任务是补件、访谈、现场核查还是纪要输出
- `deadline`
- `internal_audience`

## 最低可用输入

至少建议提供：

- 企业名称
- 行业
- 授信品种
- 金额
- 用途
- 还款来源
- 目前已拿到的材料
- 本次尽调目标
