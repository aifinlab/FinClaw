# 输入字段约定（t138 关联交易穿透）

本 skill 使用共享引擎 `shared/corporate_credit_skill_engine.py` 的 `t138` 场景。

## 最小可用输入（必须提供）

```json
{
  "company": { "name": "XX有限公司" },
  "operations": {
    "penetration_goal": "识别关联交易是否存在资金占用与利润转移",
    "related_parties": [
      { "name": "关联方A", "relation": "同一实控人" }
    ],
    "related_transactions_summary": "与关联方A存在采购与资金往来，账期偏长，期末集中结算。"
  },
  "materials": [
    { "name": "关联方清单与关系证明", "provided": true },
    { "name": "关联交易明细（合同/发票/对账单）", "provided": false }
  ]
}
```

字段说明（最小集）：

- `company.name`：企业名称
- `operations.penetration_goal`：穿透目标（决定输出范围与优先级）
- `operations.related_parties`：关联方清单（至少包含 `name`，可补 `relation`）
- `operations.related_transactions_summary`：关联交易摘要（自然语言即可）
- `materials[]`：材料清单

## 推荐补充输入（强烈建议）

- `operations.time_window`：观察窗口（如“2025Q4~2026Q1”）
- `financials.accounts_receivable_mn` / `financials.other_receivables_mn`：往来占用线索
- `operations.transaction_samples`：交易样本（若能提供结构化最好）
- `external_risks.audit_qualification`：审计意见/保留事项

