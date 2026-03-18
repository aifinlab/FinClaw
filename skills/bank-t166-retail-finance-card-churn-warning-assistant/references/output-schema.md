# 输出字段参考（t166 信用卡流失预警）

输出为结构化 JSON 或 Markdown，核心字段如下：

```json
{
  "skill_name": "bank-t166-retail-finance-card-churn-warning-assistant",
  "title": "信用卡流失预警",
  "stage": "零售经营/流失预警",
  "summary": "客户数20；高风险4，中风险6；建议先处理高风险名单并补齐授权与触达记录。",
  "recommendation": "先处理高风险/高优先人群，再逐步扩展触达。",
  "priority_list": [
    {
      "customer_id": "C001",
      "name": "张三",
      "score": 78.5,
      "segment": "高风险",
      "signals": ["近30天消费较90天均值下降超过50%", "连续45天以上无刷卡活跃"]
    }
  ],
  "action_list": ["张三（C001）: 48小时内客户经理回访+权益挽留方案，必要时升级为留存专项。"],
  "red_flags": ["有2位客户营销授权未确认，触达前需核验授权范围。"],
  "gaps": ["缺少观察时间窗口。"],
  "next_steps": ["补齐缺失字段与授权状态后再执行触达。"]
}
```
