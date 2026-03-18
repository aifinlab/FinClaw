# 输入字段约定（t136 偿债能力诊断）

本 skill 使用共享引擎 `shared/corporate_credit_skill_engine.py` 的 `t136` 场景。

## 最小可用输入（必须提供）

```json
{
  "company": { "name": "XX有限公司" },
  "financials": {
    "period": "2025年",
    "interest_bearing_debt_mn": 980.0,
    "operating_cash_flow_mn": 60.0
  },
  "operations": {
    "debt_maturity_12m_mn": 420.0
  },
  "materials": [
    { "name": "未来12个月到期表", "provided": true },
    { "name": "授信批复与用信明细", "provided": false }
  ]
}
```

字段说明（最小集）：

- `company.name`：企业名称
- `financials.interest_bearing_debt_mn`：有息负债规模（百万元）
- `financials.operating_cash_flow_mn`：经营活动现金流净额（百万元）
- `operations.debt_maturity_12m_mn`：未来12个月到期债务（百万元）
- `materials[]`：材料清单（`provided=false` 会被提示为缺失）

## 推荐补充输入（强烈建议）

- `operations.debt_maturity_3m_mn` / `operations.debt_maturity_6m_mn`：到期梯度
- `financials.cash_and_equivalents_mn`、`financials.restricted_cash_mn`
- `operations.unused_credit_line_mn`：已批授信未用额度
- `external_risks.litigation_cases`、`external_risks.asset_freeze`：诉讼与冻结
- `monitoring.covenant_breaches`：触发条款/违约事件（如有）

