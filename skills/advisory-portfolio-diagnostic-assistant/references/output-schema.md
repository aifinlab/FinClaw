# 输出结构建议

建议最终输出包含以下模块：

- 组合诊断摘要
- 收益与风险拆解
- 适配性与结构问题
- 风险提示
- 后续跟踪建议

## 建议结构化结果

~~~json
{
  "task_name": "投顾组合诊断助手",
  "summary": "",
  "key_findings": [],
  "risks": [],
  "missing_information": [],
  "recommended_actions": [],
  "appendix": {}
}
~~~

## 表达要求

- 先写结论摘要，再写证据链
- 区分已确认事实、解释性判断和待补充事项
- 对外材料相关内容必须保留复核边界
