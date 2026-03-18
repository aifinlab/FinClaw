# 输出结构口径

## 顶层字段
- `summary`：一句话摘要
- `gaps`：信息缺口列表
- `client_snapshot`：客户画像摘要
- `redemption_drivers`：赎回动因拆解
- `risk_flags`：风险提示
- `retention_options`：挽留方案清单
- `communication_flow`：沟通主线
- `compliance_notes`：合规提示与禁用表述
- `follow_up_plan`：跟进动作与留痕

## retention_options
每条包含：
- `option`：方案名称
- `when_to_use`：适用条件
- `key_message`：核心表述
- `tradeoffs`：取舍点

## communication_flow
- `opening`：开场与共情
- `facts`：事实解释
- `boundaries`：合规边界
- `options`：方案说明
- `confirmation`：确认与落地

## compliance_notes
- `must_disclose`：必须披露
- `forbidden_phrases`：禁用表述
- `wording_tips`：建议措辞
