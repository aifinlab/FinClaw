# 输入结构定义

推荐输入为 JSON 对象，适合审查岗对对公授信项目做结构化复核。

```json
{
  "company": {},
  "application": {},
  "financials": {},
  "operations": {},
  "credit_exposure": {},
  "collateral": {},
  "materials": [],
  "external_risks": {},
  "review_goals": {}
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
- `licenses_status`

### `application`

- `product_type`
- `amount_mn`
- `term_months`
- `purpose`
- `drawdown_plan`
- `repayment_source`
- `guarantee_mode`

### `financials`

- `revenue_mn`
- `net_profit_mn`
- `operating_cash_flow_mn`
- `ebitda_mn`
- `total_assets_mn`
- `total_liabilities_mn`
- `interest_bearing_debt_mn`
- `accounts_receivable_mn`
- `inventory_mn`

### `operations`

- `main_products`
- `top_customers`
- `top_suppliers`
- `order_backlog_mn`
- `contract_match_status`
- `bank_flow_match_status`
- `tax_match_status`

### `credit_exposure`

- `existing_limits_mn`
- `existing_loans_mn`
- `other_bank_borrowings_mn`
- `overdue_history`
- `guarantee_out_mn`

### `collateral`

- `collateral_type`
- `ownership_clear`
- `estimated_value_mn`
- `liquidity_comment`
- `guarantor_strength`

### `materials`

每个材料对象建议包含：

```json
{
  "name": "近三年审计报告",
  "provided": true,
  "note": "2025 年审计报告待补附注",
  "source": "客户经理"
}
```

### `external_risks`

- `litigation_cases`
- `administrative_penalties`
- `major_negative_news`
- `cross_guarantee_risk`
- `dishonest_status`
- `credit_report_flags`

### `review_goals`

- `task_type`
- `deadline`
- `audience`
- `review_stage`

## 最低可用输入

至少建议提供：

- 企业名称
- 授信品种
- 授信金额
- 用途
- 第一还款来源
- 现有材料清单
- 当前审查目标
