---
name: underlying-asset-lookthrough-assistant
description: 用于底层资产穿透尽调的结构化扫描与风险初判，覆盖资产真实性核验、数据口径一致性校对、权属与涉诉异常识别、集中度与回款压力分析。适用于信托/资管项目尽调中的资产池穿透分析、风控预审与投前复核场景。
---

# 底层资产穿透助手（T102）

## 概述

本技能面向信托项目中的底层资产穿透场景，用于对资产池做快速规则化排查，重点识别：
- 资产台账与来源口径不一致
- 资产权属瑕疵与涉诉执行风险
- 逾期与回款异常信号
- 债务人、行业、区域集中度过高风险

本技能输出为“穿透尽调初判报告”，用于辅助人工复核，不替代法律、审计和授信审批意见。

## 输入要求

支持 JSON 数组或 JSONL，每条记录对应一笔底层资产。建议字段：

- 资产标识：
  - `asset_id`
  - `asset_type`
  - `obligor_name`
  - `industry`
  - `region`
  - `as_of_date`
- 金额与口径核对：
  - `outstanding_amount`
  - `source_system_amount`
  - `trustee_file_amount`
- 质量与现金流：
  - `overdue_days`
  - `maturity_days`
  - `cashflow_status_text`
- 担保与权属：
  - `collateral_value`
  - `ltv_ratio`
  - `collateral_status_text`
  - `legal_status_text`
  - `transfer_restriction_flag`
- 完整性与关联交易：
  - `chain_complete`
  - `docs_missing_count`
  - `relation_party_flag`

## 工作流

1. 明确资产池范围、统计口径和穿透深度
2. 汇总资产台账、系统导出和托管/受托文件
3. 运行脚本进行单资产评分与组合集中度统计
4. 对高风险资产逐条核验权属、合同和现金流证据
5. 输出穿透风险报告与待补证清单

## 脚本调用指引

使用 `scripts/asset_lookthrough_analysis.py` 生成报告：

```bash
python scripts/asset_lookthrough_analysis.py \
  --input asset_pool.json \
  --output lookthrough_report.md
```

可选参数：
- `--keywords`：自定义关键词 JSON（覆盖权属/涉诉/回款关键词）
- `--top`：报告展示高风险资产数量（默认 15）

## 输出结构

1. 资产池总体概览（样本数、风险分布、平均分）
2. 集中度分析（债务人/行业/区域 Top 暴露）
3. 高风险资产清单（评分、风险命中、缺失字段）
4. 数据完整性与口径一致性问题汇总
5. 方法说明与使用限制

## 质量要求

- 每条风险判断必须能回溯到字段或关键词命中
- 明确列出缺失字段，避免隐性跳过
- 对集中度与穿透盲区要单列提示
- 不输出授信建议，仅提供尽调初判依据
