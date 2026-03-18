# 输入字段约定（t139 舆情异常预警）

本 skill 使用共享引擎 `shared/corporate_credit_skill_engine.py` 的 `t139` 场景。

## 最小可用输入（必须提供）

```json
{
  "company": { "name": "XX有限公司" },
  "operations": {
    "time_window": "2026-02-01~2026-03-15",
    "public_opinion_signals": "出现欠薪传闻、停工消息与多起合同纠纷报道，传播范围扩大。"
  },
  "external_risks": {
    "major_negative_news": "窗口期内负面新闻5条（涉诉2、欠薪2、停工1）"
  },
  "materials": [
    { "name": "舆情事件摘要与时间线", "provided": true },
    { "name": "司法/监管硬事件链接或截图", "provided": false }
  ]
}
```

字段说明（最小集）：

- `company.name`：企业名称
- `operations.time_window`：观察时间窗口（分级口径）
- `operations.public_opinion_signals`：舆情信号摘要（自然语言即可）
- `external_risks.major_negative_news`：负面舆情计数或摘要（字符串/数字都可）
- `materials[]`：材料清单

## 推荐补充输入（强烈建议）

- `external_risks.litigation_cases` / `external_risks.asset_freeze`：诉讼与冻结信息
- `monitoring.last_review_date`：最近核查日期（贷后场景）
- `operations.key_counterparties_events`：关键客户/供应商是否出现同向事件

