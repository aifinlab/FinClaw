---
name: project-feasibility-precheck-assistant
description: 用于信托项目可行性初判，基于项目结构、还款来源、担保覆盖、合规状态和历史违约信号进行规则化评分与分级。适用于投前预审、立项筛查和风控前置评估场景。
---

# 项目可行性初判助手（T104）

## 概述

本技能用于项目立项前的快速可行性初筛，输出“可行/有条件可行/暂不可行”分级，并给出主要影响因子。

## 输入要求

支持 JSON 数组或 JSONL，每条记录建议包含：

- `project_name`
- `borrower_name`
- `industry`
- `requested_amount`
- `expected_irr`
- `tenor_months`
- `collateral_coverage_ratio`
- `repayment_source_text`
- `compliance_status_text`
- `historical_default_rate`
- `sponsor_strength_score`（0-100）
- `data_completeness`（0-1）

## 工作流

1. 明确项目口径与假设前提
2. 整理核心输入字段并校验完整性
3. 运行脚本完成可行性初判评分
4. 复核关键减分项与数据可靠性
5. 输出初判结论与补充尽调建议

## 脚本调用指引

使用 `scripts/project_feasibility_precheck.py` 生成报告：

```bash
python scripts/project_feasibility_precheck.py \
  --input project_cases.json \
  --output feasibility_report.md
```

可选参数：
- `--keywords`：自定义合规/回款风险关键词
- `--top`：展示重点项目数量（默认 15）

## 输出结构

1. 总体评分分布与分级统计
2. 项目初判结果列表
3. 项目级关键加减分说明
4. 待补充信息清单
5. 方法与限制

## 质量要求

- 评分逻辑可解释
- 关键结论必须有字段依据
- 不替代正式授信审批
- 明确列出数据缺口与复核建议
