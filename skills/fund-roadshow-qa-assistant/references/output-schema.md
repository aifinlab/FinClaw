# 输出结构建议

建议最终输出包含以下模块：

- 路演Q&A清单
- 重点追问与回答边界
- 敏感问题升级建议
- 补充材料清单
- 主持串联提示

## 建议结构化结果

~~~json
{
  "task_name": "路演问答助手",
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
