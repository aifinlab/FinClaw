# 输入结构定义

推荐输入为 JSON 对象，适合国企授信判断。

```json
{
  "company": {},
  "application": {},
  "financials": {},
  "operations": {},
  "materials": [],
  "external_risks": {}
}
```

## 关键字段

- `company.name`
- `company.shareholding_chain`
- `application.amount_mn`
- `application.purpose`
- `operations.main_responsibility`
- `operations.support_document_status`
- `materials`

## 最低可用输入

- 企业名称
- 股权层级
- 申请金额
- 主责主业
- 支持文件或授权信息
