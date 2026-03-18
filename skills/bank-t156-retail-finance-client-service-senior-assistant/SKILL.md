---
name: bank-t156-retail-finance-client-service-senior-assistant
description: "Use when handling retail banking senior-customer service monitoring, vulnerability screening, and follow-up action planning; trigger for requests that need Chinese skill content with clear inputs/outputs, risk-aware wording, and optional scripts to summarize service signals."
---

# 这个 skill 是做什么的

帮助零售银行团队识别老年客群的服务风险信号与关怀机会，把客户行为、服务记录与风险提示转成可执行的触达与升级动作。输出面向客户经理、客服与运营的结构化摘要，而不是审批或处罚结论。

## 适用范围
- 老年客群服务监测、关怀回访、投诉预警与反诈提醒
- 客服、网点运营、客户经理的服务动作编排
- 适老化服务策略评估（线下/电话/线上渠道选择）

## 何时使用
- 需要对老年客户进行服务风险扫描、异常识别或关怀排序
- 需要把服务信号转为可执行动作、升级路径与跟进清单

## 何时不要使用
- 需要输出法律/合规定性、违规处罚或最终责任结论时
- 缺少客户授权或数据来源不合规时

## 默认工作流
1. 明确客群范围（年龄段、渠道、产品持有）与监测窗口
2. 汇总服务事件、投诉、风险预警与触达记录
3. 识别高优先级信号并拆分为“需立即处理/需持续跟踪/常规关怀”
4. 输出行动清单、渠道建议与升级路径
5. 标注数据缺口与待核验事项

## 输入要求
- 基础信息：`customer_id`、年龄、主要服务渠道、区域/网点
- 服务行为：近期触达时间、触达渠道、服务记录
- 风险信号：投诉次数、反诈提示、异常交易提醒
- 资产行为：余额变动、异常现金支取（若有）
- 合规授权：营销授权与联系偏好

## 输出要求
- 风险信号摘要与优先级（高/中/低）
- 推荐动作（关怀回访、线下协助、反诈提醒）
- 升级条件与责任归口建议
- 待补信息清单与数据可信度提示

## 脚本与使用方式
如需批量扫描，使用 `scripts/elder_service_scan.py` 生成结构化结果。

```bash
python scripts/elder_service_scan.py --input customers.json --output service_scan.json --as_of 2026-03-15
```

输入 JSON 示例：
```json
{
  "customers": [
    {
      "customer_id": "C001",
      "age": 67,
      "last_contact_date": "2026-01-10",
      "complaint_count_90d": 1,
      "fraud_alert_180d": 0,
      "balance_drop_30d": 15000,
      "digital_usage_score": 25,
      "branch_visit_30d": 3,
      "high_cash_withdrawal_flag": 1
    }
  ]
}
```

输出关键字段：
- `priority`：高/中/低
- `risk_score`：规则评分（仅用于排序）
- `reasons`：触发原因
- `actions`：建议动作

## 风险与边界
- 该技能只提供服务风险识别与行动建议，不替代正式合规/风控结论
- 不得基于单一信号作出惩罚或强制处置
- 必须明确数据口径、时间窗口与授权范围

## 信息不足时的处理
- 明确缺失字段并输出最小可执行建议
- 将无法验证的信息标注为“待核验”

## 输出模板（简版）
```text
客户：{customer_id}
优先级：{高/中/低}
主要信号：{reasons}
建议动作：{actions}
待补信息：{missing_fields}
```
