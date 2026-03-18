# 输入字段约定（t137 担保链风险扫描）

本 skill 使用共享引擎 `shared/corporate_credit_skill_engine.py` 的 `t137` 场景。

## 最小可用输入（必须提供）

```json
{
  "company": { "name": "XX有限公司" },
  "operations": {
    "time_window": "2025-10-01~2026-03-01",
    "guarantee_out_mn": 620.0,
    "guarantee_chain_summary": "核心企业A为B、C提供连带责任保证；B与D互保；存在循环担保迹象。"
  },
  "materials": [
    { "name": "对外担保清单（余额/期限/对象）", "provided": true },
    { "name": "担保合同与反担保材料", "provided": false }
  ]
}
```

字段说明（最小集）：

- `company.name`：企业名称
- `operations.time_window`：观察时间窗口（扫描口径）
- `operations.guarantee_out_mn`：对外担保规模（百万元）
- `operations.guarantee_chain_summary`：担保链条摘要（可用自然语言）
- `materials[]`：材料清单

## 推荐补充输入（强烈建议）

- `operations.guarantee_out_top_counterparties`：前五大被担保方（名称+余额）
- `operations.compensation_events`：是否发生代偿及次数/金额（如有）
- `external_risks.major_negative_news`：窗口期内负面事件计数/摘要
- `external_risks.litigation_cases` / `external_risks.asset_freeze`：诉讼与冻结信息

