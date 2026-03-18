---
name: bank-t180-wealth-management-asset-allocation-assistant
description: "Use when a wealth team needs to build an aggressive client allocation plan, align higher risk tolerance with target weights, and deliver rebalancing actions, product shortlist, and compliant communication notes."
---

# 进取型客户配置助手

这个 skill 面向进取型客户，强调收益潜力与风险承受能力的匹配，输出包括高权益配置比例、再平衡建议、适配产品清单与风险揭示。

## 适用范围
- 进取型客户资产配置与方案设计
- 权益为主的配置结构与风险提示
- 现有持仓诊断与再平衡建议

## 何时使用
- 客户风险承受能力较高，需要更高收益潜力配置时
- 需要输出进取型目标比例与再平衡路径时
- 需要形成可复核的适配记录时

## 何时不要使用
- 风险等级未确认或风险偏好不足
- 需要规避适当性或合规披露时

## 默认工作流
1. 复核风险等级与波动容忍度
2. 输出进取型目标配置比例与解释
3. 对比现有持仓结构，识别偏离点
4. 给出再平衡建议与节奏
5. 输出适配产品清单、风险提示与跟进动作

## 重点分析框架
- 高权益占比下的回撤容忍与止损逻辑
- 流动性与长期资金分层
- 再平衡节奏与波动管理

## 输入要求
- 客户画像（风险等级、期限、流动性、目标）
- 当前持仓：资产类别、金额、期限
- 产品池：风险等级、期限、流动性、资产类别

## 输出要求
- 目标配置比例（进取型）
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
- 不得以进取配置替代风险承受能力核验
- 配置建议不替代审批结论

## 信息不足时的处理
- 先输出缺口清单与风险提示
- 未补齐前仅给出框架建议

## 交付标准
- 适配逻辑明确、风险提示充分
- 再平衡建议可执行且可解释
- 输出可直接用于客户沟通与复核
