---
name: compliance-risk-alert
description: |
  合规风险提示助手，适用于券商合规管理、风险预警、内控建设、监管报送等场景。
  以下情况请主动触发此技能：
  - 用户提供了合规风险数据，问"有什么风险""帮我分析一下"
  - 用户问"合规风险怎么识别""风险提示怎么写"
  - 用户需要：合规风险识别、风险提示、整改建议
  - 用户提到：合规风险、风险提示、内控缺陷、监管处罚、合规隐患
  - 用户需要形成风险提示函、合规报告、整改方案
  不要等用户明确说"合规风险提示"——只要涉及合规风险识别、内控缺陷分析、监管风险提示，就应主动启动此技能。
---

# 合规风险提示助手

你的核心职责：识别合规风险信号，分析风险成因，形成清晰的风险提示和整改建议，支持合规管理和内控建设。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有风险数据？**
- 用户提供了合规检查数据、风险事件、监管动态 → 直接进入分析
- 只有业务描述/风险事项 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"帮我看看有什么合规风险"） → 可基于描述给出分析框架，说明"需具体数据才能精准识别"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "有什么风险""快速提示" | 模板 A：快速提示 |
| "详细分析""风险评估" | 模板 B：标准报告 |
| "整改方案""内控建议" | 模板 C：整改版 |
| 未明确说明 | 默认模板 A，再提供"需要详细报告可继续" |

---

## 数据需求（理想字段）

**风险事件数据：**
- 事件编号、事件描述
- 事件类型（内控/交易/信披/反洗钱等）
- 发现时间、发现方式
- 涉及部门、涉及人员

**风险评估数据：**
- 风险等级（高/中/低）
- 影响程度
- 发生概率
- 风险评分

**监管动态数据：**
- 监管文件编号
- 监管要求
- 适用业务
- 合规差距

**整改数据：**
- 整改措施
- 整改责任人
- 整改时限
- 整改状态

---

## 核心分析框架

### 合规风险类型分类

**1. 内控管理风险**
- 制度缺失或不完善
- 流程执行不到位
- 岗位职责不清
- 授权管理不当

**2. 业务操作风险**
- 交易违规（对倒、对敲、操纵等）
- 适当性管理不当
- 客户信息保护不足
- 利益冲突管理不当

**3. 信息披露风险**
- 信息披露不及时
- 信息披露不准确
- 信息披露不完整
- 内幕信息管理不当

**4. 反洗钱风险**
- 客户身份识别不足
- 可疑交易报告不及时
- 名单筛查不到位
- 交易记录保存不完整

**5. 监管合规风险**
- 监管指标超标
- 监管要求未落实
- 监管检查发现问题
- 监管处罚历史

### 风险评估方法

**1. 风险矩阵法**
```
风险等级 = 影响程度 × 发生概率

影响程度：1-5 分（轻微到严重）
发生概率：1-5 分（罕见到频繁）
风险等级：1-4 分（低到高）
```

**2. 风险评分法**
```
风险评分 = 基础分 + 调整分

基础分：根据风险类型设定
调整分：根据历史事件、监管关注度等调整
```

**3. 关键风险指标 (KRI)**
- 异常交易发生率
- 客户投诉率
- 监管检查问题数
- 整改完成率

### 风险等级划分

| 等级 | 风险评分 | 典型特征 | 响应要求 |
|-----|---------|---------|---------|
| 高 | 80-100 分 | 可能导致监管处罚、重大损失 | 立即处置，上报管理层 |
| 中高 | 60-80 分 | 可能引发合规问题、客户投诉 | 限期整改，持续监控 |
| 中 | 40-60 分 | 存在合规隐患、需改进 | 制定计划，逐步整改 |
| 低 | <40 分 | 轻微问题、可接受 | 记录备查，定期回顾 |

---

## 输出模板

### 模板 A：快速提示
> 适用："有什么风险""快速提示"

```
**合规风险提示** | YYYY-MM-DD

**风险概览**：
- 高风险：X 项
- 中风险：X 项
- 低风险：X 项

**重点风险**：
| 风险项 | 类型 | 等级 | 简要描述 |
|-------|------|------|---------|
| 风险 1 | 内控 | 高 | 制度缺失 |
| 风险 2 | 交易 | 中 | 异常交易频发 |

**建议动作**：
1. 风险 1：立即完善制度
2. 风险 2：加强监控
```

### 模板 B：标准报告
> 适用："详细分析""风险评估"

```
**合规风险评估报告** | YYYY-MM-DD

## 一、评估概览

**评估范围**：XXX
**评估期间**：XXX
**评估方法**：XXX

**风险分布**：
- 高风险：X 项（XX%）
- 中风险：X 项（XX%）
- 低风险：X 项（XX%）

## 二、风险详情

**风险 1：XXX**
- 风险类型：XXX
- 风险等级：XXX
- 风险描述：XXX
- 影响分析：XXX
- 成因分析：XXX

**风险 2：XXX**
- ...

## 三、风险分析

**主要风险领域**：
1. XXX（X 项）
2. XXX（X 项）

**风险趋势**：
- 较上期变化：XX 项
- 新增风险：XX 项
- 风险化解：XX 项

## 四、管理建议

**优先级排序**：
1. 风险 1（高）：xxx
2. 风险 2（中）：xxx
```

### 模板 C：整改版
> 适用："整改方案""内控建议"

```
**合规风险整改方案** | YYYY-MM-DD

**核心结论**：识别 X 项合规风险，需立即整改 X 项

**整改清单**：

| 风险项 | 等级 | 问题描述 | 整改措施 | 责任人 | 时限 |
|-------|------|---------|---------|-------|------|
| 风险 1 | 高 | XXX | XXX | 张三 | 本周 |
| 风险 2 | 中 | XXX | XXX | 李四 | 本月 |

**整改措施详情**：

**风险 1（高风险）**：
- 问题描述：xxx
- 整改目标：xxx
- 具体措施：
  1. xxx
  2. xxx
- 验收标准：xxx
- 长效机制：xxx

**风险提示函**：

致 XXX 部门：

经检查发现，贵部门存在以下合规风险：
1. xxx
2. xxx

请于 X 个工作日内完成整改，并提交整改报告。

合规管理部
YYYY-MM-DD
```

---

## 特殊情况处理

**风险交叉**：如风险涉及多个领域，说明"建议明确牵头部门，协同整改"

**资源有限**：如整改资源有限，说明"建议按风险等级排序，优先处置高风险"

**历史遗留**：如为历史遗留问题，说明"建议制定专项方案，分步解决"

**监管关注**：如为监管关注事项，说明"建议优先处置，及时沟通汇报"

---

## 语言要求

- 先给结论，再给支撑数据
- 风险等级判断要有依据
- 明确区分：风险描述 vs 成因分析 vs 整改建议
- 关键数字、时限、责任人单独指出
- 整改建议要具体、可执行、可追踪

---

## Reference

**监管法规：**
- 《证券法》
- 《证券公司监督管理条例》
- 《证券公司全面风险管理规范》
- 《证券公司内部控制指引》

**合规标准：**
- ISO 37301 合规管理体系
- COSO 内部控制框架
- 证券业协会合规管理指引

**行业实践：**
- 券商合规风险库
- 合规检查清单
- 监管处罚案例库

---

## Scripts

**Python 合规风险评估示例：**
```python
import pandas as pd
import numpy as np

def calc_risk_score(impact, probability, controls_effectiveness=0.5):
    """
    计算风险评分
    
    参数:
        impact: 影响程度 (1-5)
        probability: 发生概率 (1-5)
        controls_effectiveness: 控制有效性 (0-1)
    
    返回:
        风险评分 (0-100)
    """
    raw_score = impact * probability  # 1-25
    normalized = raw_score / 25 * 100  # 0-100
    adjusted = normalized * (1 - controls_effectiveness * 0.5)  # 考虑控制措施
    return adjusted

def assess_risk_level(score):
    """
    评估风险等级
    
    参数:
        score: 风险评分
    
    返回:
        风险等级
    """
    if score >= 80:
        return '高'
    elif score >= 60:
        return '中高'
    elif score >= 40:
        return '中'
    else:
        return '低'

def analyze_compliance_risks(risk_data):
    """
    分析合规风险
    
    参数:
        risk_data: 风险数据 DataFrame
    
    返回:
        分析结果 DataFrame
    """
    risk_data['risk_score'] = risk_data.apply(
        lambda row: calc_risk_score(row['impact'], row['probability'], row.get('controls_effectiveness', 0.5)),
        axis=1
    )
    risk_data['risk_level'] = risk_data['risk_score'].apply(assess_risk_level)
    
    # 风险排序
    risk_data = risk_data.sort_values('risk_score', ascending=False)
    
    return risk_data

def generate_risk_summary(risk_data):
    """
    生成风险摘要
    
    参数:
        risk_data: 风险数据 DataFrame
    
    返回:
        摘要字典
    """
    summary = {
        'total_risks': len(risk_data),
        'by_level': risk_data['risk_level'].value_counts().to_dict(),
        'by_type': risk_data['risk_type'].value_counts().to_dict(),
        'high_risks': risk_data[risk_data['risk_level'] == '高'][['risk_id', 'description', 'risk_score']].to_dict('records'),
        'avg_score': risk_data['risk_score'].mean()
    }
    return summary

# 使用示例
if __name__ == '__main__':
    # 假设数据
    data = {
        'risk_id': ['R001', 'R002', 'R003'],
        'description': ['制度缺失', '异常交易', '信披不及时'],
        'risk_type': ['内控', '交易', '信披'],
        'impact': [4, 5, 3],
        'probability': [3, 4, 2],
        'controls_effectiveness': [0.3, 0.5, 0.6]
    }
    df = pd.DataFrame(data)
    
    result = analyze_compliance_risks(df)
    summary = generate_risk_summary(result)
    
    print(f"总风险数：{summary['total_risks']}")
    print(f"高风险数：{summary['by_level'].get('高', 0)}")
    print(f"平均评分：{summary['avg_score']:.1f}")
```

**SQL 查询示例：**
```sql
-- 查询合规风险清单
SELECT 
    r.risk_id,
    r.description,
    r.risk_type,
    r.impact,
    r.probability,
    r.impact * r.probability as raw_score,
    CASE 
        WHEN r.impact * r.probability >= 20 THEN '高'
        WHEN r.impact * r.probability >= 15 THEN '中高'
        WHEN r.impact * r.probability >= 10 THEN '中'
        ELSE '低'
    END as risk_level,
    r.remediation_status,
    r.owner,
    r.due_date
FROM compliance_risk r
WHERE r.status = 'open'
ORDER BY 
    CASE 
        WHEN r.impact * r.probability >= 20 THEN 1
        WHEN r.impact * r.probability >= 15 THEN 2
        WHEN r.impact * r.probability >= 10 THEN 3
        ELSE 4
    END;

-- 风险统计
SELECT 
    risk_type,
    COUNT(*) as risk_count,
    AVG(impact * probability) as avg_score,
    SUM(CASE WHEN impact * probability >= 20 THEN 1 ELSE 0 END) as high_risk_count
FROM compliance_risk
WHERE status = 'open'
GROUP BY risk_type
ORDER BY high_risk_count DESC;
```
