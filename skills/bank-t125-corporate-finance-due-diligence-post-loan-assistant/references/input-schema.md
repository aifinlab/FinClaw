# 输入结构定义

推荐输入为 JSON 对象，适合存量授信客户贷后尽调和预警排查。

```json
{
  "company": {},
  "application": {},
  "financials": {},
  "operations": {},
  "monitoring": {},
  "collateral": {},
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

### `application`

- `product_type`
- `outstanding_balance_mn`
- `maturity_date`
- `guarantee_mode`

### `monitoring`

- `last_review_date`
- `last_review_result`
- `overdue_days`
- `fund_use_deviation`
- `covenant_breach`

### `financials`

- `revenue_mn`
- `net_profit_mn`
- `operating_cash_flow_mn`
- `accounts_receivable_mn`
- `inventory_mn`

### `materials`

每个材料对象建议包含：

```json
{
  "name": "最近一次贷后检查纪要",
  "provided": true,
  "note": "已补扫描件",
  "source": "贷后经理"
}
```

## 最低可用输入

- 企业名称
- 存量授信品种
- 授信余额
- 最近一次贷后检查日期
- 当前异常线索或监测发现
