---
name: bank-t179-wealth-management-asset-allocation-assistant
description: "Use when a wealth team needs to build a balanced client allocation plan, compare current vs target weights, and deliver rebalancing actions, product shortlist, and compliant communication notes."
---

# 平衡型客户配置助手

这个 skill 面向平衡型客户，强调在收益与回撤之间取得可解释的平衡。输出包括目标配置、现有持仓差异、再平衡路径与沟通话术。

## 适用范围
- 平衡型客户资产配置与方案比较
- 现有持仓诊断与再平衡建议
- 面向客户的沟通提纲与风险揭示

## 何时使用
- 需要在收益与波动之间做结构化配置时
- 需要输出目标比例与再平衡步骤时
- 需要输出可复核的适配记录时

## 何时不要使用
- 风险等级、期限或流动性约束未确认
- 要求规避适当性与合规披露时

## 默认工作流
1. 确认风险等级、期限与现金流约束
2. 输出平衡型目标配置比例与解释
3. 对比当前持仓结构，找出偏离点
4. 给出再平衡建议与落地顺序
5. 输出适配产品清单与沟通要点

## 重点分析框架
- 权益与固收的均衡分布
- 波动承受能力与回撤边界
- 再平衡节奏与风险暴露控制

## 输入要求
- 客户画像（风险等级、期限、流动性、目标）
- 当前持仓：资产类别、金额、期限
- 产品池：风险等级、期限、流动性、资产类别

## 输出要求
- 目标配置比例（平衡型）
- 当前配置对比与再平衡建议
- 适配产品清单与不适配原因
- 风险提示与沟通要点

## 代码与文件
- `scripts/run_skill.py`：生成配置与再平衡建议
- 共享引擎：`shared/wealth_management_skill_engine.py`

示例命令：

```bash
python scripts/run_skill.py --input assets/example-input.json --format markdown
```

## 参考资料
- `references/input-schema.md`
- `references/output-schema.md`
- `references/allocation-framework.md`
- `references/rebalancing-guidelines.md`
- `references/communication-points.md`

## 风险与边界
- 不得承诺收益或回本
- 不得忽视期限错配与流动性约束
- 配置建议不替代审批结论

## 信息不足时的处理
- 输出缺口清单并标注优先级
- 未补齐前仅给出框架建议

## 交付标准
- 配置逻辑与再平衡建议可执行
- 沟通话术明确风险边界
- 输出可以直接用于客户沟通与复核
