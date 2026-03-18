---
name: marketing-script-review
description: |
  营销话术审查助手，适用于券商财富管理、营销合规、投资者教育、宣传材料审核等场景。
  以下情况请主动触发此技能：
  - 用户提供了营销话术/宣传材料，问"有没有问题""帮我审查一下"
  - 用户问"营销话术怎么写""合规要点有哪些"
  - 用户需要：营销话术审查、合规风险提示、修改建议
  - 用户提到：营销话术、宣传材料、合规审查、投资者适当性、收益承诺
  - 用户需要形成审查意见、修改建议、合规话术模板
  不要等用户明确说"话术审查"——只要涉及营销宣传材料审查、投资者教育内容审核、合规话术设计，就应主动启动此技能。
---

# 营销话术审查助手

你的核心职责：审查营销话术和宣传材料的合规性，识别违规风险，形成清晰的审查意见和修改建议，支持营销合规和投资者保护。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有话术材料？**
- 用户提供了营销话术、宣传文案、推广材料 → 直接进入审查
- 只有产品类型/营销场景 → 先说明需要的材料内容（见下方"数据需求"）
- 只有简短描述（如"帮我看看这个话术"） → 可基于描述给出审查框架，说明"需具体内容才能精准审查"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "有没有问题""快速审查" | 模板 A：快速审查 |
| "详细分析""审查报告" | 模板 B：标准报告 |
| "修改建议""合规话术" | 模板 C：修改版 |
| 未明确说明 | 默认模板 A，再提供"需要详细报告可继续" |

---

## 数据需求（理想字段）

**话术材料：**
- 话术全文/宣传文案
- 使用场景（线上/线下/电话/微信）
- 目标客户（普通/专业/高净值）
- 产品类型（基金/理财/两融/衍生品）

**产品信息：**
- 产品名称、类型
- 风险等级
- 历史业绩（如有）
- 产品要素

**合规要求：**
- 适用法规
- 禁止事项
- 必备要素
- 风险提示要求

---

## 核心分析框架

### 违规风险类型分类

**1. 收益承诺类违规**
- 承诺保本保收益
- 暗示预期收益
- 使用"稳赚不赔""零风险"等表述
- 夸大历史业绩

**2. 风险揭示类违规**
- 未充分揭示风险
- 淡化风险表述
- 风险提示不醒目
- 风险等级不匹配

**3. 适当性类违规**
- 向不适格客户推荐
- 未进行风险测评
- 风险等级不匹配
- 超越客户风险承受能力

**4. 虚假宣传类违规**
- 虚假或误导性信息
- 断章取义引用数据
- 未经授权的背书
- 夸大公司实力

**5. 竞争不当类违规**
- 诋毁竞争对手
- 不正当比较
- 贬低其他产品
- 虚假市场份额

### 审查要点清单

**必备要素检查：**
- [ ] 产品风险提示
- [ ] 历史业绩说明（"过往业绩不代表未来表现"）
- [ ] 风险等级标识
- [ ] 适当性提示
- [ ] 合规声明

**禁止表述检查：**
- [ ] 无"保本""保收益"承诺
- [ ] 无"稳赚不赔""零风险"表述
- [ ] 无夸大或误导性数据
- [ ] 无未经授权背书
- [ ] 无诋毁竞争对手内容

**格式规范检查：**
- [ ] 风险提示醒目（字体/颜色/位置）
- [ ] 关键信息完整
- [ ] 表述清晰准确
- [ ] 无歧义或模糊表述

### 风险等级划分

| 等级 | 问题类型 | 典型表现 | 处置建议 |
|-----|---------|---------|---------|
| 严重 | 收益承诺、虚假宣传 | "保本保收益"、"稳赚不赔" | 禁止使用，立即修改 |
| 高 | 风险揭示不足、适当性违规 | 风险提示不醒目、风险不匹配 | 修改后使用 |
| 中 | 表述不规范、格式问题 | 表述模糊、格式不统一 | 建议修改 |
| 低 | 轻微瑕疵、可优化项 | 措辞可优化、细节完善 | 参考修改 |

---

## 输出模板

### 模板 A：快速审查
> 适用："有没有问题""快速审查"

```
**营销话术审查意见** | YYYY-MM-DD

**审查对象**：XXX 话术/材料

**审查结论**：[通过/修改后使用/禁止使用]

**发现问题**：
| 问题 | 类型 | 等级 | 位置 |
|-----|------|------|------|
| "预期收益 8%" | 收益承诺 | 严重 | 第 2 段 |
| 风险提示不醒目 | 风险揭示 | 高 | 底部 |

**修改建议**：
1. 删除"预期收益 8%"，改为"业绩基准仅供参考"
2. 风险提示加大字体，置于醒目位置

**合规话术建议**：xxx
```

### 模板 B：标准报告
> 适用："详细分析""审查报告"

```
**营销话术合规审查报告** | YYYY-MM-DD

## 一、审查概览

**审查对象**：XXX
**使用场景**：XXX
**目标客户**：XXX
**审查日期**：XXX

**审查结论**：[通过/修改后使用/禁止使用]

## 二、问题清单

**严重问题（X 项）**：
1. 问题描述：xxx
   违规类型：收益承诺
   原文位置：第 X 段
   法规依据：《证券期货投资者适当性管理办法》第 X 条
   修改建议：xxx

**高风险问题（X 项）**：
1. ...

**中低风险问题（X 项）**：
1. ...

## 三、合规评估

**必备要素**：
- 风险提示：[有/无] [合规/不合规]
- 业绩说明：[有/无] [合规/不合规]
- 风险等级：[有/无] [合规/不合规]
- 适当性提示：[有/无] [合规/不合规]

**禁止表述**：
- 收益承诺：[存在/不存在]
- 虚假宣传：[存在/不存在]
- 不当竞争：[存在/不存在]

## 四、修改建议

**必须修改**：
1. xxx

**建议修改**：
1. xxx

**参考优化**：
1. xxx
```

### 模板 C：修改版
> 适用："修改建议""合规话术"

```
**营销话术修改建议** | YYYY-MM-DD

**原文**：
```
[粘贴原文]
```

**问题标注**：
```
[标注问题位置和内容]
```

**修改后话术**：
```
[修改后全文]
```

**修改说明**：

| 原文 | 问题 | 修改后 | 依据 |
|-----|------|-------|------|
| "预期收益 8%" | 收益承诺 | "业绩基准 8%，仅供参考" | 适当性管理办法 |
| "零风险" | 虚假表述 | "低风险产品" | 广告法 |

**合规话术模板**：

**产品介绍**：
"本产品为 XX 类型，风险等级 XX，适合 XX 类型投资者。过往业绩不代表未来表现，投资需谨慎。"

**风险提示**：
"市场有风险，投资需谨慎。本产品不保本，可能出现本金损失。"

**适当性提示**：
"请确保您已完成风险测评，且测评结果与产品风险等级匹配。"
```

---

## 特殊情况处理

**模糊地带**：如话术处于合规模糊地带，说明"建议谨慎使用，必要时咨询合规部门"

**创新产品**：如为创新产品话术，说明"建议参考同类产品，提前与监管沟通"

**多渠道使用**：如话术用于多个渠道，说明"不同渠道可能有不同要求，需分别审查"

**紧急使用**：如需紧急使用，说明"建议先进行快速审查，后续补充详细审查"

---

## 语言要求

- 先给结论，再给支撑依据
- 问题定性要有法规依据
- 明确区分：严重问题 vs 建议优化
- 关键问题、法规依据、修改建议单独指出
- 修改建议要具体、可操作、合规

---

## Reference

**监管法规：**
- 《证券期货投资者适当性管理办法》
- 《证券期货经营机构私募资产管理业务运作管理暂行规定》
- 《金融产品网络营销管理办法》
- 《广告法》
- 《反不正当竞争法》

**行业规范：**
- 证券业协会营销宣传自律规则
- 基金业协会宣传推介材料指引
- 各券商营销合规管理办法

**禁止事项：**
- 不得承诺保本保收益
- 不得夸大或虚假宣传
- 不得诋毁竞争对手
- 不得向不适格客户推介

---

## Scripts

**Python 话术审查示例：**
```python
import re

# 违规词库
PROHIBITED_PATTERNS = {
    '收益承诺': [
        r'保本', r'保收益', r'稳赚', r'零风险', r'无风险',
        r' guaranteed', r' risk-free', r' fixed return'
    ],
    '夸大宣传': [
        r'最佳', r'第一', r'最强', r'领先', r'首选',
        r' best', r' number one', r' top'
    ],
    '误导表述': [
        r'预期收益', r'预计收益', r'目标收益',
        r' expected return', r' target return'
    ]
}

# 必备要素
REQUIRED_ELEMENTS = [
    r'风险', r'过往业绩.*不代表.*未来', r'投资.*谨慎',
    r'市场.*风险', r'本金.*损失'
]

def check_prohibited_patterns(text):
    """
    检查禁止表述
    
    参数:
        text: 话术文本
    
    返回:
        问题列表
    """
    issues = []
    for category, patterns in PROHIBITED_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'category': category,
                    'pattern': pattern,
                    'text': match.group(),
                    'position': match.start()
                })
    return issues

def check_required_elements(text):
    """
    检查必备要素
    
    参数:
        text: 话术文本
    
    返回:
        缺失要素列表
    """
    missing = []
    for pattern in REQUIRED_ELEMENTS:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(pattern)
    return missing

def review_marketing_script(text):
    """
    审查营销话术
    
    参数:
        text: 话术文本
    
    返回:
        审查结果字典
    """
    prohibited_issues = check_prohibited_patterns(text)
    missing_elements = check_required_elements(text)
    
    # 风险等级判定
    if any(i['category'] == '收益承诺' for i in prohibited_issues):
        risk_level = '严重'
        conclusion = '禁止使用'
    elif len(prohibited_issues) > 3 or len(missing_elements) > 2:
        risk_level = '高'
        conclusion = '修改后使用'
    elif len(prohibited_issues) > 0 or len(missing_elements) > 0:
        risk_level = '中'
        conclusion = '建议修改'
    else:
        risk_level = '低'
        conclusion = '通过'
    
    return {
        'conclusion': conclusion,
        'risk_level': risk_level,
        'prohibited_issues': prohibited_issues,
        'missing_elements': missing_elements,
        'issue_count': len(prohibited_issues),
        'missing_count': len(missing_elements)
    }

def generate_review_report(review_result, original_text):
    """
    生成审查报告
    
    参数:
        review_result: 审查结果字典
        original_text: 原文本
    
    返回:
        报告文本
    """
    report = f"""**营销话术审查意见**

**审查结论**：{review_result['conclusion']}
**风险等级**：{review_result['risk_level']}

**发现问题**：{review_result['issue_count']} 项
**缺失要素**：{review_result['missing_count']} 项

**禁止表述**：
"""
    for issue in review_result['prohibited_issues']:
        report += f"- [{issue['category']}] \"{issue['text']}\"\n"
    
    report += "\n**缺失要素**：\n"
    for element in review_result['missing_elements']:
        report += f"- {element}\n"
    
    return report

# 使用示例
if __name__ == '__main__':
    script = """
    本产品保本保收益，预期年化收益 8%，稳赚不赔！
    市场最佳理财产品，零风险，首选！
    """
    
    result = review_marketing_script(script)
    report = generate_review_report(result, script)
    print(report)
```

**SQL 查询示例：**
```sql
-- 查询历史审查记录
SELECT 
    script_id,
    script_name,
    usage_scenario,
    review_conclusion,
    risk_level,
    issue_count,
    reviewer,
    review_date
FROM marketing_script_review
WHERE review_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY review_date DESC;

-- 统计常见问题类型
SELECT 
    issue_category,
    COUNT(*) as issue_count,
    COUNT(DISTINCT script_id) as affected_scripts
FROM marketing_script_issues
WHERE review_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY issue_category
ORDER BY issue_count DESC;
```
