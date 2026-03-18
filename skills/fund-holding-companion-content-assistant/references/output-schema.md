# 输出结构建议

建议最终输出包含以下模块：

- 陪伴内容摘要
- 事实解释
- 情绪安抚表述
- 后续关注点
- 敏感边界提示

## 建议结构化结果

~~~json
{
  "task_name": "客户陪伴内容助手",
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
