---
name: bank-t160-retail-finance-pre-check-assistant
description: "Use when performing retail consumer-loan pre-checks, eligibility screening, and document gap analysis; trigger for requests that need Chinese skill content with structured precheck logic and optional scripts." 
---

# 这个 skill 是做什么的

面向消费贷业务的预审初筛与资料缺口识别，输出“可推进/待补资料/阻断”的初步判断、关键风险提示与补件清单，用于前置沟通与材料整理。

## 适用范围
- 消费贷申请初筛与资料完整性检查
- 客户经理面谈前的风险点整理
- 运营团队的补件追踪

## 何时使用
- 需要快速判断消费贷申请是否具备推进条件
- 需要列出补件清单与核验重点

## 何时不要使用
- 需要输出最终授信与审批结论
- 缺少基本资料却要求确定性判断

## 默认工作流
1. 确认申请主体、用途与金额区间
2. 检查关键准入字段与资料完整性
3. 分出阻断项与待核验项
4. 输出补件清单与沟通重点

## 输入要求
- 主体信息：`applicant_id`、年龄、职业、居住稳定性
- 收入与负债：月收入、负债收入比
- 征信信息：信用评分、逾期记录
- 贷款信息：申请金额、用途、期限

## 输出要求
- 初筛结论与理由
- 阻断项、待核验项
- 补件清单与面谈重点
- 数据口径与时间窗口说明

## 脚本与使用方式
批量预审使用 `scripts/precheck_consumer.py`。

```bash
python scripts/precheck_consumer.py --input consumer_applications.json --output consumer_precheck.json
```

输入 JSON 示例：
```json
{
  "applications": [
    {
      "applicant_id": "A002",
      "age": 29,
      "credit_score": 630,
      "debt_to_income": 0.45,
      "monthly_income": 12000,
      "loan_amount": 80000,
      "income_verified": true
    }
  ]
}
```

输出关键字段：
- `result`：可推进/待补资料/阻断
- `blockers`：阻断项
- `needs_verify`：需人工核验
- `missing_fields`：缺失字段

## 风险与边界
- 预审不等于审批结论
- 不得基于不完整数据做确定性判断
- 不得虚构监管要求或政策口径

## 信息不足时的处理
- 输出“待补资料”并列出优先级
- 提示可补采集渠道

## 输出模板（简版）
```text
申请人：{applicant_id}
初筛结论：{result}
阻断项：{blockers}
待核验：{needs_verify}
缺失字段：{missing_fields}
```
