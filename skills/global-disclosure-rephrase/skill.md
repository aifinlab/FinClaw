---
name: global-disclosure-rephrase
description: 用于披露重述场景。适用于金融工作中的基础任务单元。
---

# Global Skill: 上市企业披露替代表述生成（公网可查数据）

## 数据来源
本 Skill 使用公网可查、可访问的数据来源构建规则底座与样例检索能力，主要包括：

1. **中国证监会（CSRC）**
   - 《上市公司信息披露管理办法（证监会令第182号）》
   - 《公开发行证券的公司信息披露内容与格式准则第2号——年度报告的内容与格式（2021年修订）》

2. **上海证券交易所（SSE）**
   - 《上海证券交易所股票上市规则（2025年4月修订）》

3. **深圳证券交易所（SZSE）**
   - 信息披露评价、自律监管与行业信息披露相关公开规则

4. **巨潮资讯（CNINFO）公开公告检索**
   - 用于检索上市公司的历史公告标题和公开披露记录，辅助判断既有披露口径与本次表述的衔接关系

> 说明：本 Skill 依赖公网访问。若公开站点接口、网页结构或反爬策略变化，脚本可能需要同步调整。

## 功能
本 Skill 面向**单个上市企业**的披露文本场景，提供以下能力：

1. **法规基线查询**
   - 输出适用于上市公司信息披露的一般规则底座
   - 汇总与披露表述、完整性、可理解性相关的公开法规来源

2. **企业公告公开记录检索**
   - 基于股票代码检索公开历史公告
   - 用于辅助识别当前拟披露内容是否与既往公告口径不一致

3. **替代表述生成**
   - 对输入的原始披露文本生成更加规范、审慎、可审阅的替代表述
   - 重点处理模糊时间、弱化不利事实、过度确定性承诺、定性多定量少等问题

4. **风险提示**
   - 对原始文本打出潜在披露风险标签，例如：
     - 弱化不利事实
     - 缺少时间边界
     - 缺少量化口径
     - 预测性表述风险
     - 治理或程序口径不足

## 使用示例

### 1）命令行直接运行
```bash
python script/disclosure_rephrase.py \
  --company "贵州茅台" \
  --stock-code 600519 \
  --text "受市场波动影响，公司相关业务短期波动，不会产生重大影响，公司将及时推进相关事项。"
```

### 2）输出到 JSON 文件
```bash
python script/disclosure_rephrase.py \
  --company "宁德时代" \
  --stock-code 300750 \
  --text "项目推进过程中存在一定压力，但总体风险可控，后续将及时披露。" \
  --start-date 2025-01-01 \
  --end-date 2026-03-13 \
  --output result.json
```

### 3）典型输出内容
输出 JSON 中通常包含：
- 企业名称、股票代码
- 原始文本
- 建议替代表述
- 风险标签与原因
- 法规基线清单
- 近期公告标题列表
- 合规提示

## 交易说明
本 Skill 用于**上市公司信息披露文本的研究、规范化改写与初步合规检查**，不用于投资建议，也不用于交易指令生成。

请特别注意：

1. **不得用于掩盖重大不利事实**
   - 替代表述的目标是提高披露质量，不是回避披露义务
   - 对重大风险、重大诉讼、重大合同变化、业绩预告修正、关联交易、资金占用、违规担保等事项，不得使用模糊措辞替代依法应披露内容

2. **不得替代正式法律或审计意见**
   - 本 Skill 不是律师意见、审计意见、保荐机构核查意见，也不是交易所审核结论

3. **建议人工复核**
   - 对以下情形建议由法务、证券事务、董秘办公室或外部中介复核：
     - 业绩敏感事项
     - 重大资产重组
     - 再融资
     - 退市风险
     - 行业监管高敏感事项
     - 涉嫌误导性陈述或重大遗漏的情形

4. **适用边界**
   - 该工具更适合用于：
     - 公告草稿审阅
     - 风险提示增强
     - 统一披露口径
     - 对外答复材料的披露一致性预检查

## License
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
