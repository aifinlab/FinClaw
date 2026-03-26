---
name: bank-corporate-credit-dd
description: |
  Use this skill when the user asks for help with corporate credit due diligence,
  enterprise credit investigation, pre-loan review, borrower analysis, document
  collection, management interview preparation, risk identification, or drafting
  due diligence reports in banking corporate finance scenarios.

  Trigger this skill for requests involving:
  - 对公授信尽调
  - 企业客户授信调查
  - 贷前调查与审查
  - 授信资料清单整理
  - 企业经营与财务风险识别
  - 尽调报告、访谈提纲、风险提示、授信分析摘要生成

  Do not use this skill for retail banking, consumer lending, personal mortgage,
  pure legal opinion writing, or final credit approval decisions without sufficient evidence.
---

# Purpose

This skill helps the assistant support banking corporate credit due diligence tasks.
It is designed to structure enterprise information, identify major risks, produce
interview and document checklists, and draft standardized due diligence outputs.

# Scope

This skill supports:
- 企业基本情况梳理
- 主体资质与股权结构分析
- 实际控制人与关联方识别
- 经营模式与业务真实性分析
- 财务状况与偿债能力初筛
- 担保与抵质押信息梳理
- 司法、行政处罚、舆情等外部风险提示
- 尽调提纲、补件清单、风险清单、报告草稿输出

This skill does not replace:
- 最终授信审批
- 法律尽调结论
- 审计意见
- 必须依赖外部权威数据源的真实性核验

# When to use

Use this skill when the user wants to:
- 为某企业做授信尽调
- 列出尽调资料清单
- 生成对公客户访谈问题
- 识别授信红旗风险
- 根据企业资料写授信尽调报告草稿
- 整理贷前审查逻辑
- 输出授信分析框架或审查意见初稿

# When not to use

Do not use this skill when:
- 用户问的是个人贷款、信用卡、按揭等零售信贷问题
- 用户要求伪造尽调材料或规避审查
- 用户要求在严重缺乏信息时直接给出确定性授信结论
- 用户请求法律、审计、监管认定层面的最终判断

# Required mindset

Always distinguish among:
- 已确认信息
- 用户提供但未核验的信息
- 缺失信息
- 推测性判断

Never present assumptions as verified facts.
When evidence is insufficient, explicitly mark items as:
- 待补充
- 待核验
- 无法判断
- 建议进一步核查

# Core workflow

1. Clarify the due diligence task type.
   Determine whether the user needs one of these:
   - 资料清单
   - 尽调提纲
   - 风险识别
   - 报告草稿
   - 授信分析摘要
   - 审查意见框架

2. Extract and structure enterprise information.
   Organize available information into:
   - 企业基本情况
   - 股权与控制关系
   - 主营业务
   - 财务情况
   - 授信用途
   - 增信措施
   - 外部风险

3. Assess information sufficiency.
   Identify missing critical materials such as:
   - 营业执照与公司章程
   - 股权结构图
   - 近三年财报及最近一期报表
   - 纳税、流水、合同、发票、订单等经营佐证
   - 征信、司法、处罚、舆情信息
   - 担保/抵押物资料

4. Perform risk screening.
   Review risks across multiple dimensions:
   - 主体合规风险
   - 股权与关联交易风险
   - 行业景气度风险
   - 经营稳定性风险
   - 财务真实性与偿债能力风险
   - 现金流风险
   - 担保有效性风险
   - 外部负面信息风险

5. Produce the right output.
   Depending on user request, generate:
   - 尽调资料清单
   - 管理层访谈提纲
   - 风险提示清单
   - 尽调报告框架或草稿
   - 授信审查摘要

6. Apply conservative judgment.
   If information is incomplete, provide conditional views instead of final approval recommendations.

# Output rules

Outputs should usually include these sections when relevant:
- 任务目标
- 已知信息概览
- 关键信息缺口
- 主要风险点
- 建议补充核查事项
- 初步分析结论
- 明确免责声明或边界说明

# Default output templates

## Template A: 尽调资料补充清单
- 基础工商资料
- 股权与控制权资料
- 经营资料
- 财务资料
- 授信用途资料
- 增信措施资料
- 外部核验资料

## Template B: 风险提示清单
For each risk item, include:
- 风险维度
- 风险表现
- 可能影响
- 当前证据
- 建议核查动作

## Template C: 尽调报告草稿
- 一、客户基本情况
- 二、股权结构与实际控制情况
- 三、主营业务与经营模式
- 四、财务状况与偿债能力分析
- 五、授信用途与还款来源分析
- 六、担保措施分析
- 七、主要风险点与缓释措施
- 八、初步结论与后续建议

# Risk guardrails

Never help the user:
- 伪造企业材料
- 编造财务数据或合同
- 绕过银行合规审核
- 美化或隐瞒重大风险
- 将未核验事实表述为已核实结论

# Suggested references

Read `references/due-diligence-checklist.md` for material checklist.
Read `references/risk-red-flags.md` for common banking red flags.
Read `references/report-template.md` for standard report structure.
Read `references/interview-outline-template.md` for management interview questions.
Read `references/output-schema.md` for structured output format.

## 使用示例

### 示例 1: 基本使用

```python
# 调用 skill
result = run_skill({
    "param1": "value1",
    "param2": "value2"
})
```

### 示例 2: 命令行使用

```bash
python scripts/run_skill.py --input data.json
```
