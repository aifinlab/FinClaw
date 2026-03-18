---
name: bank-t158-retail-finance-installment-marketing-assistant
description: "Use when planning retail credit-card installment marketing, customer segmentation, and outreach prioritization; trigger for requests that need Chinese skill content with clear inputs/outputs, compliance-aware actions, and optional scripts for segmentation." 
---

# 这个 skill 是做什么的

用于信用卡分期营销的客群分层、触达策略与行动清单输出，确保动作合规、可执行且可复盘。

## 适用范围
- 分期营销活动策划与名单初筛
- 分期客群分层、优先级排序与渠道匹配
- 营销结果的结构化复盘与指标口径说明

## 何时使用
- 需要把交易与还款数据转成分期营销行动方案
- 需要基于客户特征与风险信号设计分层触达

## 何时不要使用
- 要求绕过授权/频控/适当性规则
- 未给出营销目标或可执行渠道时

## 默认工作流
1. 明确营销目标、产品口径与活动周期
2. 汇总客群特征、交易行为、还款表现与风险标记
3. 进行分层排序并说明依据
4. 输出分层动作、话术方向与指标口径

## 输入要求
- 客户基础：`customer_id`、卡片类型、额度区间
- 行为数据：近3月最大单笔消费、转化/分期历史
- 还款表现：按时还款率、逾期次数
- 合规约束：营销授权、频控规则、投诉记录

## 输出要求
- 客群分层（高/中/低潜）与排序
- 对应的触达方式与优惠策略
- 风险提示与禁入客群说明
- 指标口径（转化率、分期金额、投诉率）

## 脚本与使用方式
批量分层使用 `scripts/installment_marketing_segment.py`。

```bash
python scripts/installment_marketing_segment.py --input installment_candidates.json --output installment_segmented.json
```

输入 JSON 示例：
```json
{
  "customers": [
    {
      "customer_id": "C003",
      "largest_purchase_3m": 9000,
      "revolving_ratio": 0.6,
      "installment_history": 2,
      "on_time_rate_12m": 0.99,
      "risk_flag": 0
    }
  ]
}
```

输出关键字段：
- `segment`：高潜/中潜/低潜
- `score`：分层评分（用于排序）
- `offer`：推荐优惠策略

## 风险与边界
- 分层建议不等于强制营销或收益承诺
- 必须遵守营销授权与触达频控要求
- 需要清楚标注数据口径与时间窗口

## 信息不足时的处理
- 输出分层框架和待补数据清单
- 数据不足时默认“低潜/观察”

## 输出模板（简版）
```text
客户：{customer_id}
分层：{segment}
建议策略：{offer}
理由：{reasons}
待补信息：{missing_fields}
```
