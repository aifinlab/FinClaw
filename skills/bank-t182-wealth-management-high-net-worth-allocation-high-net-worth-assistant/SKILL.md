---
name: bank-t182-wealth-management-high-net-worth-allocation-high-net-worth-assistant
description: "Use when a wealth team needs to design high-net-worth client allocations, translate family goals and constraints into layered buckets, and output a compliant allocation plan with rebalancing steps and product shortlist."
---

# 高净值资产配置助手

这个 skill 用于高净值客户的分层资产配置与方案落地，把家族目标、风险承受能力、流动性需求、币种结构与现有持仓统一成可执行、可复核、可沟通的配置建议。

## 适用范围
- 高净值客户的资产配置方案设计与复核
- 多目标、跨周期资金安排（现金流、教育、养老、传承）
- 分层资产配置与再平衡建议
- 需要形成主方案与备选方案的对比输出

## 何时使用
- 需要把“家族目标 + 风险边界 + 流动性约束”转为分层配置方案
- 客户已有持仓且需要再平衡路径时
- 需要输出可合规留痕的沟通要点与风险提示

## 何时不要使用
- 风险等级、期限或流动性信息未确认即要求做强结论
- 需要规避适当性、税务或合规要求的情形

## 默认工作流
1. 复核客户画像与关键约束（风险等级、期限、流动性、AUM、家族目标）
2. 以“流动性/核心稳健/成长/多元/保障与传承”五层结构给出目标配置比例
3. 对比现有持仓结构，识别偏离点与再平衡动作
4. 输出主方案与备选方案，并说明触发条件
5. 给出适配产品清单、风险披露要点与后续跟进清单

## 重点分析框架
- 资金分层：短期现金流、中长期增值、保障与传承的边界
- 目标映射：家族目标与配置桶的对应关系
- 结构约束：单一资产集中度、流动性锁定期、币种结构
- 风险说明：波动容忍与回撤边界、替代方案触发条件

## 输入要求
- 客户画像：风险等级、期限、流动性、AUM、家族目标
- 现有持仓：资产类别、金额、期限、流动性
- 产品池：风险等级、期限、流动性、资产类别
- 约束与偏好：集中度限制、币种结构、税务或传承约束

## 输出要求
- 分层配置目标比例与逻辑说明
- 当前配置对比与再平衡动作
- 适配产品清单与不适配原因
- 风险提示、沟通要点与下一步动作
- 主方案/备选方案的取舍理由与触发条件

## 代码与文件
- `scripts/run_skill.py`：生成高净值分层配置建议与产品适配清单
- 共享引擎：`shared/wealth_management_skill_engine.py`

示例命令：

```bash
python scripts/run_skill.py --input assets/example-input.json --format markdown
```

## 参考资料
- `references/input-schema.md`
- `references/output-schema.md`
- `references/hnw-allocation-framework.md`
- `references/liquidity-bucket-guidelines.md`
- `references/risk-disclosure-points.md`

## 风险与边界
- 不得承诺收益或回本
- 不得在缺少关键约束时给出强结论
- 配置建议不替代审批结论或产品尽调

## 信息不足时的处理
- 先输出缺口清单与核验重点
- 未补齐前仅给出分层框架与备选方案

## 交付标准
- 目标配置与再平衡建议可执行且可解释
- 风险提示充分、适当性边界清晰
- 输出可直接用于客户沟通与合规复核
