# 输入字段约定（t135 现金流压力诊断）

本 skill 使用共享引擎 `shared/corporate_credit_skill_engine.py` 的 `t135` 场景。

## 最小可用输入（必须提供）

```json
{
  "company": {
    "name": "XX有限公司"
  },
  "financials": {
    "period": "2025年",
    "operating_cash_flow_mn": -120.0,
    "net_profit_mn": 80.0,
    "accounts_receivable_mn": 560.0
  },
  "materials": [
    { "name": "近三期财务报表", "provided": true },
    { "name": "应收账款明细/账龄", "provided": false }
  ]
}
```

字段说明（最小集）：

- `company.name`：企业名称
- `financials.operating_cash_flow_mn`：经营活动现金流净额（百万元口径）
- `financials.net_profit_mn`：净利润（百万元口径）
- `financials.accounts_receivable_mn`：应收账款余额（百万元口径）
- `materials[]`：材料清单，`provided=false` 的会被纳入“关键材料未提供”提示

## 推荐补充输入（强烈建议）

用于把“可能原因”落到证据链与行动：

- `financials.revenue_mn`、`gross_profit_mn`、`inventory_mn`、`prepayments_mn`
- `financials.capex_mn`（资本开支/购建固定资产等）
- `operations.period`（若 `financials.period` 未给）
- `operations.debt_maturity_12m_mn`（未来12个月到期债务）
- `operations.receivable_turnover_days` / `inventory_turnover_days`（如有）
- `external_risks.audit_qualification`（审计意见/保留事项，如有）

## 可选结构（不会强制，但可提升质量）

- `application.product_type`：若本次诊断用于授信/贷后特定产品，可补充（不会强制）。
- `monitoring.last_review_date`：若是贷后场景，建议提供最近核查日期。

