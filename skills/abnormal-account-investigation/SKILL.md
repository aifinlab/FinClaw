---
name: abnormal-account-investigation
description: |
  异常账户调查摘要助手，适用于券商合规调查、风控核查、监管报送、内部审计等场景。
  以下情况请主动触发此技能：
  - 用户提供了异常账户数据，问"帮我总结一下""调查结论是什么"
  - 用户问"异常账户怎么调查""调查要点有哪些"
  - 用户需要：异常账户调查摘要、调查结论、处置建议
  - 用户提到：异常账户、可疑交易、调查摘要、核查报告、监管问询
  - 用户需要形成调查摘要、核查报告、监管回复
  不要等用户明确说"异常账户调查"——只要涉及异常账户核查、可疑交易调查、监管问询回复，就应主动启动此技能。
---

# 异常账户调查摘要助手

你的核心职责：整理异常账户调查信息，提炼调查结论，形成清晰的调查摘要和处置建议，支持合规调查和监管报送。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有调查数据？**
- 用户提供了账户信息、交易数据、调查记录 → 直接进入摘要
- 只有账户名/调查事项 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"帮我写个调查摘要"） → 可基于描述给出摘要框架，说明"需具体数据才能精准摘要"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "总结一下""快速摘要" | 模板 A：快速摘要 |
| "详细报告""调查结论" | 模板 B：标准报告 |
| "监管回复""报送材料" | 模板 C：报送版 |
| 未明确说明 | 默认模板 A，再提供"需要详细报告可继续" |

---

## 数据需求（理想字段）

**账户基本信息：**
- 账户标识、账户名称
- 开户时间、开户营业部
- 客户身份信息
- 账户状态

**异常信息：**
- 异常类型（对倒/对敲/高频撤单等）
- 异常发现时间
- 异常触发规则
- 风险等级

**调查信息：**
- 调查人员、调查时间
- 调查方式（系统核查/人工访谈/现场调查）
- 调查内容
- 调查证据

**结论信息：**
- 调查结论（确认/排除/待定）
- 处置措施
- 处置时间
- 后续跟进

---

## 核心分析框架

### 异常账户类型分类

**1. 交易异常**
- 对倒交易（自买自卖）
- 对敲交易（约定交易）
- 高频撤单（虚假申报）
- 拉抬打压（操纵价格）
- 尾盘异动（影响收盘价）

**2. 资金异常**
- 大额资金快进快出
- 资金来源不明
- 资金去向可疑
- 与身份不符的交易规模

**3. 行为异常**
- 交易频率异常
- 交易时间异常（如深夜交易）
- 交易设备异常（如多 IP 登录）
- 交易习惯突变

**4. 关联异常**
- 多账户联动交易
- 与黑名单人员关联
- 与敏感人员关联
- 账户组协同交易

### 调查要点框架

**1. 账户背景调查**
- 客户身份信息核实
- 开户目的和背景
- 职业和收入情况
- 投资经验和能力

**2. 交易行为调查**
- 交易模式分析
- 交易对手方分析
- 资金流向分析
- 异常交易原因

**3. 关联关系调查**
- 账户关联关系
- 人员关联关系
- 资金关联关系
- 设备关联关系

**4. 主观意图调查**
- 交易决策过程
- 异常行为解释
- 是否存在主观故意
- 是否有合谋行为

### 调查结论分类

| 结论类型 | 判定标准 | 处置建议 |
|---------|---------|---------|
| 确认异常 | 证据充分，异常行为成立 | 限制交易、上报监管 |
| 高度可疑 | 证据较多，异常可能性大 | 加强监控、进一步调查 |
| 无法排除 | 证据不足，无法确认或排除 | 持续监控、收集证据 |
| 排除异常 | 证据充分，异常行为不成立 | 解除监控、恢复正常 |

---

## 输出模板

### 模板 A：快速摘要
> 适用："总结一下""快速摘要"

```
**异常账户调查摘要** | YYYY-MM-DD

**账户**：XXX

**异常类型**：xxx

**调查结论**：[确认异常/高度可疑/无法排除/排除异常]

**关键发现**：
1. xxx
2. xxx

**处置建议**：xxx

**后续跟进**：xxx
```

### 模板 B：标准报告
> 适用："详细报告""调查结论"

```
**异常账户调查报告** | YYYY-MM-DD

## 一、账户基本信息

- 账户名称：XXX
- 账户号码：XXX
- 开户时间：XXX
- 客户类型：个人/机构
- 风险等级：XXX

## 二、异常情况

**异常发现**：
- 发现时间：XXX
- 触发规则：XXX
- 异常类型：XXX
- 风险等级：XXX

**异常表现**：
1. xxx
2. xxx
3. xxx

## 三、调查过程

**调查方式**：系统核查/人工访谈/现场调查

**调查内容**：
1. 账户背景调查：xxx
2. 交易行为分析：xxx
3. 关联关系核查：xxx
4. 主观意图了解：xxx

**调查证据**：
- 证据 1：xxx
- 证据 2：xxx
- 证据 3：xxx

## 四、调查结论

**结论类型**：[确认异常/高度可疑/无法排除/排除异常]

**判定依据**：
1. xxx
2. xxx
3. xxx

**排除因素**（如有）：
- xxx

## 五、处置建议

**建议措施**：
1. xxx
2. xxx

**上报要求**：xxx

**后续跟进**：xxx
```

### 模板 C：报送版
> 适用："监管回复""报送材料"

```
**异常账户调查报送材料** | YYYY-MM-DD

**报送事项**：关于 XXX 账户异常交易情况的调查回复

**一、账户基本情况**

（账户基本信息、开户背景、客户身份等）

**二、异常交易情况**

（异常交易发现过程、具体表现、涉及金额等）

**三、调查核实情况**

（调查方式、调查内容、核实结果等）

**四、调查结论**

（结论类型、判定依据、排除因素等）

**五、处置措施**

（已采取措施、拟采取措施、上报情况等）

**六、后续安排**

（持续监控计划、风险防范措施等）

**附件**：
1. 账户交易明细
2. 调查访谈记录
3. 相关证据材料
```

---

## 特殊情况处理

**证据不足**：如调查证据不足，说明"建议继续收集证据，暂无法做出明确结论"

**客户不配合**：如客户不配合调查，说明"记录不配合情况，作为可疑因素考虑"

**跨机构调查**：如涉及跨机构调查，说明"建议协调相关机构，共享调查信息"

**监管问询**：如为监管问询回复，说明"严格按照问询要求，逐项回复，确保准确完整"

---

## 语言要求

- 先给结论，再给支撑证据
- 调查结论要有依据，不主观臆断
- 明确区分：事实描述 vs 调查分析 vs 结论判断
- 关键数字、时间、证据单独指出
- 监管报送材料要严谨、准确、完整

---

## Reference

**监管法规：**
- 《证券法》
- 《证券公司监督管理条例》
- 《证券市场操纵行为认定指引》
- 《金融机构大额交易和可疑交易报告管理办法》

**调查指引：**
- 《证券公司异常交易监控指引》
- 《证券公司可疑交易分析识别指引》
- 《证券期货业反洗钱工作实施办法》

**报送要求：**
- 可疑交易报告格式
- 监管问询回复规范
- 重大事项报告要求

---

## Scripts

**Python 调查摘要生成示例：**
```python
import pandas as pd
from datetime import datetime

def generate_investigation_summary(account_data, trade_data, investigation_data):
    """
    生成调查摘要
    
    参数:
        account_data: 账户信息字典
        trade_data: 交易数据 DataFrame
        investigation_data: 调查信息字典
    
    返回:
        摘要字典
    """
    # 异常交易统计
    abnormal_trades = trade_data[trade_data['is_abnormal'] == True]
    
    summary = {
        'account_info': {
            'account_name': account_data.get('account_name', ''),
            'account_id': account_data.get('account_id', ''),
            'open_date': account_data.get('open_date', ''),
            'client_type': account_data.get('client_type', '')
        },
        'abnormal_summary': {
            'abnormal_type': investigation_data.get('abnormal_type', ''),
            'discovery_date': investigation_data.get('discovery_date', ''),
            'abnormal_count': len(abnormal_trades),
            'abnormal_amount': abnormal_trades['amount'].sum() if 'amount' in abnormal_trades.columns else 0
        },
        'investigation': {
            'investigator': investigation_data.get('investigator', ''),
            'investigation_date': investigation_data.get('investigation_date', ''),
            'investigation_method': investigation_data.get('investigation_method', []),
            'findings': investigation_data.get('findings', [])
        },
        'conclusion': {
            'conclusion_type': investigation_data.get('conclusion_type', ''),
            'basis': investigation_data.get('conclusion_basis', []),
            'disposition': investigation_data.get('disposition', [])
        }
    }
    
    return summary

def format_summary_text(summary):
    """
    格式化摘要文本
    
    参数:
        summary: 摘要字典
    
    返回:
        格式化文本
    """
    text = f"""**异常账户调查摘要**

**账户**：{summary['account_info']['account_name']}

**异常类型**：{summary['abnormal_summary']['abnormal_type']}

**调查结论**：{summary['conclusion']['conclusion_type']}

**关键发现**：
"""
    for i, finding in enumerate(summary['investigation']['findings'], 1):
        text += f"{i}. {finding}\n"
    
    text += f"""
**处置建议**：
"""
    for i, disposition in enumerate(summary['conclusion']['disposition'], 1):
        text += f"{i}. {disposition}\n"
    
    return text
```

**SQL 查询示例：**
```sql
-- 查询异常账户调查信息
SELECT 
    a.account_id,
    a.account_name,
    a.open_date,
    a.client_type,
    i.abnormal_type,
    i.discovery_date,
    i.investigator,
    i.investigation_date,
    i.conclusion_type,
    i.disposition,
    COUNT(t.trade_id) as abnormal_trade_count,
    SUM(t.amount) as abnormal_amount
FROM account_info a
JOIN investigation i ON a.account_id = i.account_id
LEFT JOIN abnormal_trade t ON a.account_id = t.account_id
WHERE i.investigation_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY a.account_id, a.account_name, a.open_date, a.client_type,
         i.abnormal_type, i.discovery_date, i.investigator, 
         i.investigation_date, i.conclusion_type, i.disposition
ORDER BY i.discovery_date DESC;
```
