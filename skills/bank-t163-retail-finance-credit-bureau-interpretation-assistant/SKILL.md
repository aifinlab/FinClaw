---
name: bank-t163-retail-finance-credit-bureau-interpretation-assistant
description: "用于银行零售金融场景的征信报告解读与风险要点梳理，当需要将征信指标翻译为业务可执行的关注点与追问方向时触发。"
---

# 征信解读助手

## 这个 skill 是做什么的
将征信摘要中的查询、逾期、多头、负债结构等指标进行结构化解读，输出风险关注点、驱动项说明、追问方向与待核验事项，帮助客户经理或贷前人员形成“可行动”的征信解读意见。

## 适用范围
- 零售贷款征信解读、贷前预审与尽调准备
- 客户经理、零售运营、贷前审核辅助团队
- 需要结构化输出征信要点与后续核验方向

## 何时使用
- 有征信摘要或征信报告结构化字段时
- 需要将征信指标转化为业务语言与面谈提纲时

## 何时不要使用
- 无任何征信数据时
- 需要正式征信审批结论或法律判断时

## 默认工作流
1. 明确征信报告时间、口径与适用产品
2. 识别核心风险指标（逾期、查询、多头、负债）
3. 拆解异常成因与可能驱动项
4. 输出关注点、追问方向与核验建议

## 输入要求
- 征信摘要字段（查询次数、逾期情况、账户数、负债余额、使用率等）
- 报告时间与样本范围
- 业务场景（经营贷/消费贷等）

## 输出要求
- 征信解读摘要（事实）
- 风险关注点与可能成因（推断需标注）
- 追问方向与补充资料建议
- 待核验事项清单

## 风险与边界
- 不得把相关性直接写成因果关系
- 不得把解读结论当作审批结论
- 数据缺失必须标注并降级处理

## 信息不足时的处理
- 输出可解释范围内的事实与趋势
- 列出缺失字段并给出补充建议

## 配套脚本
- `scripts/credit_bureau_interpretation.py`：读取征信摘要与阈值配置，输出关注点与追问方向。

### 脚本使用
```bash
python scripts/credit_bureau_interpretation.py --input bureau.json --rules rules.json --output out.json
```

### bureau.json 示例结构
```json
{
  "report_date": "2026-01-15",
  "summary": {
    "inquiries_3m": 6,
    "inquiries_6m": 9,
    "delinquencies_12m": 1,
    "max_dpd_24m": 30,
    "revolving_utilization": 0.78,
    "open_accounts": 12,
    "total_balance": 260000
  }
}
```

### rules.json 示例结构
```json
{
  "thresholds": {
    "max_inquiries_3m": 5,
    "max_utilization": 0.7,
    "max_delinquencies_12m": 0
  }
}
```

### out.json 输出要点
- `flags`：命中阈值的风险点
- `interpretation`：业务解读摘要
- `questions`：建议追问方向
- `missing_fields`：缺失字段

## 交付标准
- 清楚区分事实、解释与推断
- 输出可直接用于面谈或补充材料准备
