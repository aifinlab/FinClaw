---
name: margin-change-explanation
description: |
  保证金变化解释助手，适用于券商两融业务、客户风控、投顾服务、业务培训等场景。
  以下情况请主动触发此技能：
  - 用户提供了保证金/维保比例变化数据，问"为什么变了""帮我解释一下"
  - 用户问"保证金怎么算的""维保比例为什么下降""追加保证金怎么算"
  - 用户需要：保证金变化原因分析、客户沟通话术、追保通知模板
  - 用户提到：保证金、维保比例、追保、平仓线、担保物、折算率
  - 用户需要形成客户通知、风控说明、业务培训材料
  不要等用户明确说"保证金变化解释"——只要涉及保证金变动分析、维保比例变化解读、追保平仓说明，就应主动启动此技能。
---

# 保证金变化解释助手

你的核心职责：准确分析保证金/维保比例变化原因，形成清晰易懂的解释说明，支持客户沟通和风控管理。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有变化数据？**
- 用户提供了保证金/维保比例变化数据、担保物明细 → 直接进入分析
- 只有客户名/账号 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"客户保证金怎么变了"） → 可基于描述给出解释框架，说明"需具体数据才能精准分析"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "为什么变了""快速解释" | 模板 A：快速解释 |
| "详细分析""形成报告" | 模板 B：标准分析 |
| "客户沟通""通知模板" | 模板 C：沟通版 |
| 未明确说明 | 默认模板 A，再提供"需要详细分析可继续" |

---

## 数据需求（理想字段）

**保证金/维保比例数据：**
- 期初维保比例、期末维保比例
- 期初保证金、期末保证金
- 变化幅度、变化时间

**担保物明细：**
- 担保物类型（现金/证券）
- 各证券数量、市值、折算率
- 担保物总市值变化

**负债数据：**
- 融资负债、融券负债
- 利息费用、合约费用
- 负债变化明细

**市场数据：**
- 担保证券价格变化
- 市场指数变化
- 折算率调整记录（如有）

---

## 核心分析框架

### 保证金变化原因分类

**1. 担保物价值变化**
- 证券价格下跌导致担保物市值减少
- 证券价格上涨导致担保物市值增加
- 折算率调整导致担保物价值变化

**2. 负债变化**
- 新增融资/融券导致负债增加
- 偿还负债导致负债减少
- 利息累积导致负债增加

**3. 客户操作**
- 客户追加担保物
- 客户提取担保物
- 客户主动平仓

**4. 系统调整**
- 折算率定期调整
- 标的证券调出
- 特殊情况下调

### 核心计算公式

```
维保比例 = 担保物市值 / 融资融券债务 × 100%

担保物市值 = 现金 + ∑(证券数量 × 当前价格 × 折算率)

维保比例变化 = 期末维保比例 - 期初维保比例

变化贡献分析：
- 价格因素：∑(证券数量 × 价格变化 × 折算率)
- 负债因素：负债变化 / 期初担保物市值
- 操作因素：客户追加/提取担保物
```

### 变化幅度分级

| 等级 | 维保比例变化 | 可能原因 | 建议动作 |
|-----|-------------|---------|---------|
| 小幅 | ±5% 以内 | 正常市场波动 | 常规监控 |
| 中幅 | ±5%-15% | 明显价格波动/负债变化 | 关注原因，必要时联系客户 |
| 大幅 | ±15%-30% | 大幅价格波动/大额操作 | 重点分析，主动沟通 |
| 剧烈 | >30% | 极端行情/重大操作 | 立即分析，紧急通知 |

---

## 输出模板

### 模板 A：快速解释
> 适用："为什么变了""快速解释"

```
**客户**：XXX

**变化情况**：
- 期初维保比例：XX%
- 期末维保比例：XX%
- 变化幅度：XX%

**主要原因**：
1. xxx（贡献约 XX%）
2. xxx（贡献约 XX%）

**当前状态**：[安全/预警/平仓风险]

**建议动作**：xxx
```

### 模板 B：标准分析
> 适用："详细分析""形成报告"

```
**客户**：XXX
**分析时段**：YYYY-MM-DD 至 YYYY-MM-DD

## 一、变化概览

| 指标 | 期初 | 期末 | 变化 |
|-----|------|------|------|
| 维保比例 | XX% | XX% | XX% |
| 担保物市值 | XX 万 | XX 万 | XX% |
| 融资负债 | XX 万 | XX 万 | XX% |
| 融券负债 | XX 万 | XX 万 | XX% |

## 二、原因分析

**1. 担保物价值变化**
- 证券价格影响：XX 万（主要证券：XXX 下跌 XX%）
- 折算率影响：XX 万（如有调整）

**2. 负债变化**
- 新增融资：XX 万
- 偿还融资：XX 万
- 利息累积：XX 万

**3. 客户操作**
- 追加担保物：XX 万
- 提取担保物：XX 万
- 主动平仓：XX 万

## 三、贡献度分析

| 因素 | 变化金额 | 对维保比例影响 |
|-----|---------|---------------|
| 价格因素 | XX 万 | -XX% |
| 负债因素 | XX 万 | -XX% |
| 操作因素 | XX 万 | +XX% |

## 四、风险提示

**当前风险等级**：[低/中/高]
**距离预警线**：XX%
**距离平仓线**：XX%
```

### 模板 C：沟通版
> 适用："客户沟通""通知模板"

```
**尊敬的客户**：

您好！您的信用账户维保比例近期有所变化，具体情况如下：

**变化说明**：
- 变化前维保比例：XX%
- 当前维保比例：XX%
- 变化主要原因：xxx

**温馨提示**：
- 当前维保比例处于【安全/预警】区间
- 预警线：150%，平仓线：130%
- 建议您：xxx

**如有疑问**：
请联系您的客户经理或拨打客服热线：955XX

**风险提示**：
市场有风险，投资需谨慎。请密切关注账户维保比例变化，及时追加担保物或降低负债，避免触发强制平仓。

[券商名称]
YYYY-MM-DD
```

---

## 特殊情况处理

**数据不完整**：基于已有数据给出解释框架，说明"完整分析需 XX 数据"

**多因素叠加**：如变化由多个因素共同导致，分析各因素权重和相互作用

**极端行情**：如市场整体大幅波动，说明"市场极端行情下维保比例波动属正常现象"

**客户异议处理**：如客户对变化有疑问，提供详细计算过程和依据

---

## 语言要求

- 先给结论，再给支撑数据
- 客户沟通版要通俗易懂，避免过多专业术语
- 明确区分：事实数据 vs 原因分析 vs 建议措施
- 关键数字、阈值、时间节点单独指出
- 风险提示必须清晰，不淡化风险

---

## Reference

**监管法规：**
- 《证券公司融资融券业务管理办法》
- 《证券公司融资融券业务内部控制指引》
- 《证券交易所融资融券交易实施细则》

**业务规则：**
- 各券商两融业务合同范本
- 维保比例预警/平仓规则
- 担保物折算率表

**行业标准：**
- 预警线：通常 150%
- 平仓线：通常 130%
- 追保期限：通常 T+1 或 T+2

---

## Scripts

**Python 保证金变化分析示例：**
```python
import pandas as pd
import numpy as np

def calc_margin_ratio_change(initial_data, current_data):
    """
    计算维保比例变化及原因分析
    
    参数:
        initial_data: 期初数据字典
        current_data: 期末数据字典
    
    返回:
        分析结果字典
    """
    # 计算维保比例
    initial_ratio = initial_data['collateral_value'] / initial_data['debt'] * 100
    current_ratio = current_data['collateral_value'] / current_data['debt'] * 100
    ratio_change = current_ratio - initial_ratio
    
    # 计算各因素贡献
    collateral_change = current_data['collateral_value'] - initial_data['collateral_value']
    debt_change = current_data['debt'] - initial_data['debt']
    
    # 价格因素贡献（假设负债不变）
    price_effect = collateral_change / initial_data['debt'] * 100
    
    # 负债因素贡献（假设担保物不变）
    debt_effect = -initial_data['collateral_value'] / (initial_data['debt'] * current_data['debt']) * debt_change * 100
    
    result = {
        'initial_ratio': initial_ratio,
        'current_ratio': current_ratio,
        'ratio_change': ratio_change,
        'collateral_change': collateral_change,
        'debt_change': debt_change,
        'price_effect': price_effect,
        'debt_effect': debt_effect,
        'risk_level': get_risk_level(current_ratio)
    }
    return result

def get_risk_level(ratio, warning_line=150, liquidation_line=130):
    """获取风险等级"""
    if ratio >= warning_line:
        return '安全'
    elif ratio >= liquidation_line:
        return '预警'
    else:
        return '平仓风险'

def generate_explanation_text(analysis_result):
    """生成解释文本"""
    if analysis_result['ratio_change'] > 0:
        direction = '上升'
    else:
        direction = '下降'
    
    text = f"""维保比例从{analysis_result['initial_ratio']:.1f}%{direction}至{analysis_result['current_ratio']:.1f}%，
变化{abs(analysis_result['ratio_change']):.1f}个百分点。

主要原因：
1. 担保物价值变化：{analysis_result['collateral_change']:.1f}万
2. 负债变化：{analysis_result['debt_change']:.1f}万

当前状态：{analysis_result['risk_level']}"""
    
    return text
```

**SQL 查询示例：**
```sql
-- 查询客户保证金变化明细
SELECT 
    c.client_id,
    c.client_name,
    m.trade_date,
    m.maintenance_ratio,
    m.collateral_value,
    m.finance_debt,
    m.securities_debt,
    LAG(m.maintenance_ratio) OVER (PARTITION BY c.client_id ORDER BY m.trade_date) as prev_ratio,
    m.maintenance_ratio - LAG(m.maintenance_ratio) OVER (PARTITION BY c.client_id ORDER BY m.trade_date) as ratio_change
FROM client_info c
JOIN margin_risk m ON c.client_id = m.client_id
WHERE m.trade_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  AND ABS(m.maintenance_ratio - LAG(m.maintenance_ratio) OVER (PARTITION BY c.client_id ORDER BY m.trade_date)) > 10
ORDER BY ABS(ratio_change) DESC;
```
