---
name: bank-t157-retail-finance-limit-increase-opportunity-assistant
description: "Use when identifying retail credit-card limit increase opportunities or prioritizing outreach; trigger for requests that need Chinese skill content with clear eligibility checks, ranking logic, and optional scripts for scoring." 
---

# 这个 skill 是做什么的

用于识别信用卡提额机会、排序潜力客户并输出触达建议与风控边界。它只做“机会识别与优先级建议”，不替代授信审批与最终额度决策。

## 适用范围
- 信用卡提额机会挖掘与客户排序
- 营销触达策略设计与提额名单初筛
- 客户经理和运营团队的提额机会周报/日报

## 何时使用
- 需要根据交易、还款、负债等数据筛选提额机会
- 需要形成提额名单、建议动作与风险提示

## 何时不要使用
- 要求直接给出最终授信额度或审批结论时
- 数据不完整且无法满足最低审核字段时

## 默认工作流
1. 明确提额目标与适用客群（产品类型、额度区间、政策约束）
2. 汇总还款表现、额度使用率、负债情况与风险标记
3. 计算评分与排序，区分“建议提额/观察/暂缓”
4. 输出触达动作、需补验证与风险提示

## 输入要求
- 基础字段：`customer_id`、现有额度、卡片类型
- 行为与还款：近3个月消费均值、还款准时率、逾期记录
- 风险指标：风险标记、拒贷/拒额记录（如有）
- 收入与负债：月收入、负债率或授信总额（如有）

## 输出要求
- 提额机会评分与排序
- 触达建议与优先级
- 风险提示与待核验事项
- 触达话术与频控提示（若有）

## 脚本与使用方式
批量评分使用 `scripts/limit_increase_scoring.py`。

```bash
python scripts/limit_increase_scoring.py --input limit_candidates.json --output limit_scored.json
```

输入 JSON 示例：
```json
{
  "customers": [
    {
      "customer_id": "C002",
      "credit_limit": 20000,
      "avg_spend_3m": 16000,
      "on_time_rate_12m": 0.99,
      "delinquency_12m": 0,
      "monthly_income": 15000,
      "debt_to_income": 0.35,
      "risk_flag": 0
    }
  ]
}
```

输出关键字段：
- `decision`：建议提额/可观察/暂缓
- `score`：规则评分（用于排序）
- `reasons`：主要触发因素

## 风险与边界
- 评分仅用于机会识别，不能替代授信审批
- 不得将营销建议包装为审批结论或额度承诺
- 需标注数据口径与时间窗口

## 信息不足时的处理
- 列出缺失字段与可补采集方式
- 输出“观察”级别建议而非强结论

## 输出模板（简版）
```text
客户：{customer_id}
评分：{score}
建议：{decision}
理由：{reasons}
待补信息：{missing_fields}
```
