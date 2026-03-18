# 技能组合映射参考

## 输入侧技能

- `underwriting-summary-report-assistant` 负责把原始材料压缩成可阅读的案件底稿
- `underwriting-question-list-assistant` 负责把疑点转成追问项
- `underwriting-supplement-request-assistant` 负责把信息缺口转成补件动作
- `underwriting-rules-qa-assistant` 负责把规则文本转成可用口径

## 输出侧技能

- `underwriting-review-opinion-assistant` 负责把前述材料收束成复核意见
- `underwriting-conclusion-explanation-assistant` 负责把阶段性结论转成可沟通表达

## 编排原则

- 摘要是底座，但不是每次都必须重新生成
- 规则问答只在存在规则边界问题时插入
- 结论解释通常在复核意见之后或已有结论时使用
- 如果用户已提供某个技能产物，应优先吸收，不要重复重做