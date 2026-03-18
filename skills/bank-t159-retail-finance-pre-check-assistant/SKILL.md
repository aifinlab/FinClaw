---
name: bank-t159-retail-finance-pre-check-assistant
description: "Use when performing retail mortgage pre-checks or document gap analysis before formal approval; trigger for requests that need Chinese skill content with structured precheck logic, outputs, and optional scripts." 
---

# 这个 skill 是做什么的

面向房贷业务的预审初筛与资料梳理，输出“可推进/待补资料/阻断”级别的初步判断、关键风险提示与补件清单，服务客户经理与运营团队的前置沟通。

## 适用范围
- 房贷准入前的资料完整性检查
- 房贷申请初筛与风险提示
- 运营或客户经理的面谈准备与补件清单

## 何时使用
- 需要快速判断房贷申请是否具备推进条件
- 需要输出结构化补件与核验清单

## 何时不要使用
- 要求输出最终审批或授信结论
- 缺少关键事实却要求确定性结论

## 默认工作流
1. 确认申请主体、房产信息与资金用途
2. 检查关键准入字段与资料完整性
3. 按“阻断项/待核验项/可推进项”分类
4. 输出补件清单与面谈要点

## 输入要求
- 主体信息：`applicant_id`、年龄、职业、婚姻/家庭情况
- 资产与负债：收入证明、负债收入比、授信存量
- 征信信息：信用评分、逾期记录
- 房产信息：房屋类型、首付比例、交易真实性材料

## 输出要求
- 初筛结论：`可推进/待补资料/阻断`
- 阻断项与待核验项
- 补件清单与面谈重点
- 数据口径与时间窗口说明

## 脚本与使用方式
批量预审使用 `scripts/precheck_mortgage.py`。

```bash
python scripts/precheck_mortgage.py --input mortgage_applications.json --output mortgage_precheck.json
```

输入 JSON 示例：
```json
{
  "applications": [
    {
      "applicant_id": "A001",
      "age": 35,
      "credit_score": 680,
      "debt_to_income": 0.42,
      "down_payment_ratio": 0.35,
      "property_type": "住宅",
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
- 预审仅为前置筛查，不可替代审批结论
- 不得基于不完整数据输出确定性结论
- 不得虚构监管口径或政策要求

## 信息不足时的处理
- 明确缺失字段与建议补采方式
- 输出“待补资料”并列出优先级

## 输出模板（简版）
```text
申请人：{applicant_id}
初筛结论：{result}
阻断项：{blockers}
待核验：{needs_verify}
缺失字段：{missing_fields}
```
