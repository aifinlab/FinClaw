---
name: bank-t178-wealth-management-asset-allocation-assistant
description: "Use when a wealth team needs to build a conservative client allocation plan, combine current holdings with target weights, and produce rebalancing actions, product shortlist, and compliant communication notes."
---

# 稳健型客户配置助手

这个 skill 面向稳健型财富客户，重点在于“风险可控、流动性可解释、收益路径清晰”。输出包括目标配置、现有持仓对比、再平衡建议、适配产品清单以及沟通话术。

## 适用范围
- 稳健型客户资产配置方案设计
- 现有持仓诊断与再平衡建议
- 方案可沟通化输出（风险提示、跟进动作）

## 何时使用
- 需要输出稳健型目标配置与资产比例建议时
- 需要结合现有持仓给出再平衡路径时
- 需要形成可直接沟通的配置说明与风险提示时

## 何时不要使用
- 客户风险等级或资金期限未确认
- 用户要求绕开适当性或合规披露

## 默认工作流
1. 明确客户风险等级、期限、流动性目标与资金用途
2. 输出稳健型目标配置比例，并解释比例来源
3. 汇总现有持仓，形成现状对比
4. 给出再平衡方向（增加/降低比例）
5. 输出适配产品清单、风险提示与行动清单

## 重点分析框架
- 保本不保收益：稳健偏好下的风险上限
- 固收为主、权益为辅，预留充足流动性
- 再平衡优先考虑期限与回撤约束

## 输入要求
- 客户风险等级、期限、流动性需求、目标用途
- 当前持仓：资产类别、金额、期限
- 产品池：风险等级、期限、流动性、资产类别、标签

## 输出要求
- 目标配置比例（稳健型）
- 当前配置对比与再平衡建议
- 适配产品清单与不适配产品原因
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
- 不得忽视流动性约束与期限错配
- 配置建议不替代审批结论

## 信息不足时的处理
- 明确缺口并输出可执行的补充清单
- 先输出框架与风险提示，待补齐后再给出最终比例

## 交付标准
- 配置逻辑可解释、可复核
- 再平衡建议可执行
- 沟通话术包含风险提示与下一步动作
