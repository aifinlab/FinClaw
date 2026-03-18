# 输入结构定义

推荐输入为 JSON 对象，适合上下游客户识别。

```json
{
  "company": {},
  "operations": {},
  "materials": [],
  "external_risks": {}
}
```

## 关键字段

- `company.name`
- `operations.identification_target`
- `operations.time_window`
- `operations.transaction_samples`
- `operations.sample_coverage`
- `operations.customer_concentration`

## 最低可用输入

- 核心主体名称
- 识别目标
- 时间窗口
- 交易或名单样本
