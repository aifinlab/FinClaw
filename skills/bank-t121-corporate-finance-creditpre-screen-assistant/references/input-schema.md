# 输入结构定义

推荐输入为一个 JSON 对象。允许字段不完整，但关键字段缺失时脚本会自动下调结论强度。

## 顶层结构

```json
{
  "company": {},
  "application": {},
  "financials": {},
  "operations": {},
  "materials": [],
  "external_risks": {},
  "credit_support": {}
}
```

## `company`

```json
{
  "name": "企业名称",
  "unified_credit_code": "统一社会信用代码",
  "industry": "行业",
  "region": "区域",
  "years_in_operation": 8,
  "registered_capital_mn": 120.0,
  "shareholder_structure": [
    {
      "shareholder": "股东名称",
      "holding_ratio": 60.0
    }
  ],
  "actual_controller": "实际控制人",
  "customer_level": "存量/新增/白名单/观察类"
}
```

## `application`

```json
{
  "product_type": "流动资金贷款",
  "amount_mn": 30.0,
  "term_months": 12,
  "purpose": "采购原材料",
  "repayment_source": "销售回款",
  "guarantee_mode": "保证+设备抵押",
  "requested_stage": "预审"
}
```

## `financials`

```json
{
  "period": "2025Q4",
  "revenue_mn": 380.0,
  "net_profit_mn": 18.0,
  "operating_cash_flow_mn": 9.5,
  "ebitda_mn": 31.0,
  "interest_expense_mn": 6.2,
  "total_assets_mn": 260.0,
  "total_liabilities_mn": 168.0,
  "current_assets_mn": 150.0,
  "current_liabilities_mn": 110.0,
  "interest_bearing_debt_mn": 96.0,
  "accounts_receivable_mn": 88.0,
  "inventory_mn": 42.0
}
```

## `operations`

```json
{
  "main_products": ["汽车零部件", "模具组件"],
  "top_customer_ratio_pct": 42.0,
  "top_supplier_ratio_pct": 31.0,
  "contract_coverage_months": 7,
  "order_backlog_mn": 86.0,
  "invoice_match_status": "基本匹配",
  "bank_flow_match_status": "需补充解释",
  "related_party_sales_ratio_pct": 6.0
}
```

## `materials`

每个材料对象建议包含：

```json
{
  "name": "营业执照",
  "provided": true,
  "date": "2025-12-31",
  "note": "扫描件清晰"
}
```

常见材料包括：

- 营业执照
- 公司章程
- 股权结构图
- 最近三年财务报表
- 最近一期财务报表
- 审计报告
- 纳税申报或完税证明
- 主要合同 / 发票 / 订单
- 银行流水
- 征信授权
- 董事会 / 股东会决议
- 抵押物资料 / 保证资料

## `external_risks`

```json
{
  "litigation_cases": 2,
  "litigation_amount_mn": 4.3,
  "administrative_penalties": 1,
  "penalty_severity": "一般",
  "dishonest_status": false,
  "major_negative_news": false,
  "overdue_history": false,
  "cross_guarantee_risk": true
}
```

## `credit_support`

```json
{
  "guarantor": "保证人名称",
  "collateral_type": "设备抵押",
  "collateral_value_mn": 28.0,
  "margin_mn": 0.0,
  "shareholder_support": "实控人提供连带责任保证"
}
```

## 最低可用输入

如果只能提供最低可用输入，至少建议包括：

- `company.name`
- `company.industry`
- `application.product_type`
- `application.amount_mn`
- `application.purpose`
- `application.repayment_source`
- `financials.revenue_mn`
- `financials.net_profit_mn`
- `financials.total_assets_mn`
- `financials.total_liabilities_mn`

缺少这些字段时，输出应主要聚焦“信息缺口”和“下一步补件建议”。
