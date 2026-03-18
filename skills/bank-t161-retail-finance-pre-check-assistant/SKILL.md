---
name: bank-t161-retail-finance-pre-check-assistant
description: "Use when performing retail small-business loan pre-checks, eligibility screening, and document gap analysis; trigger for requests that need Chinese skill content with structured precheck logic and optional scripts." 
---

# 这个 skill 是做什么的

用于经营贷（小微/个体）预审初筛与资料缺口识别，输出“可推进/待补资料/阻断”的初步判断、关键风险提示与补件清单，帮助客户经理快速判断是否进入尽调。

## 适用范围
- 经营贷申请初筛与资料完整性检查
- 经营主体基本面与现金流初步判断
- 面谈准备与补件清单生成

## 何时使用
- 需要快速判断经营贷申请是否具备推进条件
- 需要列出补件清单、核验重点与风险提示

## 何时不要使用
- 需要输出最终授信与审批结论
- 缺少关键经营信息仍要求确定性结论

## 默认工作流
1. 明确经营主体、经营年限与资金用途
2. 检查核心资料与口径一致性
3. 识别阻断项与待核验项
4. 输出补件清单与核验重点

## 输入要求
- 主体信息：`applicant_id`、经营年限、行业、工商信息
- 经营规模：年收入、主要客户/订单
- 现金流：覆盖倍数、资金用途
- 合规信息：税务合规、涉诉情况

## 输出要求
- 初筛结论与理由
- 阻断项、待核验项
- 补件清单与面谈重点
- 数据口径与时间窗口说明

## 脚本与使用方式
批量预审使用 `scripts/precheck_business.py`。

```bash
python scripts/precheck_business.py --input business_applications.json --output business_precheck.json
```

输入 JSON 示例：
```json
{
  "applications": [
    {
      "applicant_id": "A003",
      "business_years": 3,
      "annual_revenue": 800000,
      "cashflow_coverage": 1.3,
      "tax_compliance": true,
      "legal_dispute_flag": 0
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
- 不得基于不完整数据输出确定性判断
- 不得虚构监管或政策口径

## 信息不足时的处理
- 输出“待补资料”并列出优先级
- 对关键字段缺失要明确标注

## 输出模板（简版）
```text
申请人：{applicant_id}
初筛结论：{result}
阻断项：{blockers}
待核验：{needs_verify}
缺失字段：{missing_fields}
```
