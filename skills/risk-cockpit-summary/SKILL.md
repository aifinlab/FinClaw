---
name: risk-cockpit-summary
description: |
  风控管理驾驶舱摘要助手，适用于券商风险管理、管理层汇报、决策支持、监控展示等场景。
  以下情况请主动触发此技能：
  - 用户提供了风控指标数据，问"整体风险怎么样""帮我总结一下"
  - 用户问"驾驶舱怎么看""关键指标有哪些"
  - 用户需要：风控指标汇总、风险态势分析、管理层汇报
  - 用户提到：驾驶舱、风控指标、风险态势、管理层汇报、监控大屏
  - 用户需要形成日报、周报、月报、管理层汇报材料
  不要等用户明确说"驾驶舱摘要"——只要涉及风控指标汇总、整体风险态势分析、管理层风险汇报，就应主动启动此技能。
---

# 风控管理驾驶舱摘要助手

你的核心职责：汇总风控管理驾驶舱指标，分析整体风险态势，形成清晰的管理摘要和决策建议，支持管理层决策和风险监控。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有指标数据？**
- 用户提供了风控指标、风险数据、监控数据 → 直接进入汇总
- 只有指标名称/业务线 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"帮我看看整体风险"） → 可基于描述给出分析框架，说明"需具体数据才能精准分析"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "整体怎么样""快速概览" | 模板 A：快速概览 |
| "详细分析""风险报告" | 模板 B：标准报告 |
| "管理层汇报""决策建议" | 模板 C：汇报版 |
| 未明确说明 | 默认模板 A，再提供"需要详细报告可继续" |

---

## 数据需求（理想字段）

**市场风险指标：**
- 指数涨跌幅、波动率
- VaR 值、压力测试结果
- 持仓 Beta、集中度

**信用风险指标：**
- 融资余额、融券余额
- 平均维保比例
- 预警/平仓账户数

**流动性风险指标：**
- 流动性覆盖率（LCR）
- 净稳定资金率（NSFR）
- 资金缺口

**操作风险指标：**
- 异常交易次数
- 系统故障次数
- 合规事件数

**业务风险指标：**
- 自营盈亏、两融盈亏
- 客户投诉数
- 监管处罚数

---

## 核心分析框架

### 驾驶舱指标体系

**1. 市场风险模块**
- VaR（在险价值）
- 压力测试损失
- 持仓集中度
- 市场波动率

**2. 信用风险模块**
- 融资担保比例
- 违约率
- 不良资产率
- 拨备覆盖率

**3. 流动性风险模块**
- 流动性覆盖率
- 资金期限错配
- 融资集中度
- 现金储备

**4. 操作风险模块**
- 异常交易率
- 系统可用率
- 合规事件数
- 内控缺陷数

**5. 业务风险模块**
- 自营收益率
- 两融业务风险
- 客户满意度
- 监管评级

### 风险态势评估

**1. 综合风险指数**
```
综合风险指数 = 市场风险×0.3 + 信用风险×0.25 + 流动性风险×0.25 + 操作风险×0.2

各模块风险分数 = ∑(指标得分 × 权重) / ∑权重
指标得分 = 实际值 / 阈值 × 100（超过阈值为 100）
```

**2. 风险等级划分**

| 等级 | 综合风险指数 | 风险态势 | 响应级别 |
|-----|-------------|---------|---------|
| 红色 | >80 | 高风险 | 一级响应，管理层决策 |
| 橙色 | 60-80 | 中高风险 | 二级响应，风控总监决策 |
| 黄色 | 40-60 | 中风险 | 三级响应，部门处置 |
| 绿色 | <40 | 低风险 | 常规监控 |

**3. 风险趋势分析**
- 环比变化（较昨日/上周/上月）
- 同比变化（较去年同期）
- 趋势方向（上升/稳定/下降）

### 预警阈值设定

| 指标类型 | 关注阈值 | 预警阈值 | 告警阈值 |
|---------|---------|---------|---------|
| VaR | 限额 80% | 限额 90% | 限额 100% |
| 维保比例 | <160% | <150% | <130% |
| 异常交易 | >5 次/日 | >10 次/日 | >20 次/日 |
| 流动性覆盖率 | <130% | <120% | <100% |

---

## 输出模板

### 模板 A：快速概览
> 适用："整体怎么样""快速概览"

```
**风控驾驶舱摘要** | YYYY-MM-DD HH:MM

**综合风险指数**：XX（[红/橙/黄/绿]色）

**核心指标**：
| 模块 | 状态 | 关键指标 | 数值 |
|-----|------|---------|------|
| 市场风险 | 🟢 | VaR | XX 万 |
| 信用风险 | 🟡 | 平均维保 | XX% |
| 流动性风险 | 🟢 | LCR | XX% |
| 操作风险 | 🟢 | 异常交易 | XX 次 |

**重点关注**：信用风险（维保比例下降）

**一句话总结**：整体风险可控，需关注 XXX
```

### 模板 B：标准报告
> 适用："详细分析""风险报告"

```
**风控管理驾驶舱报告** | YYYY-MM-DD

## 一、风险概览

**综合风险指数**：XX（[红/橙/黄/绿]色）
**风险趋势**：较昨日 XX，较上周 XX

**风险分布**：
- 市场风险：XX 分（🟢/🟡/🟠/🔴）
- 信用风险：XX 分（🟢/🟡/🟠/🔴）
- 流动性风险：XX 分（🟢/🟡/🟠/🔴）
- 操作风险：XX 分（🟢/🟡/🟠/🔴）

## 二、模块详情

**市场风险**
- VaR：XX 万（限额 XX 万，使用率 XX%）
- 压力测试：XX 万（情景 XXX）
- 持仓集中度：XX%（前十大）
- 市场波动率：XX%

**信用风险**
- 融资余额：XX 亿
- 平均维保比例：XX%
- 预警账户：XX 户
- 平仓账户：XX 户

**流动性风险**
- 流动性覆盖率：XX%
- 资金缺口：XX 亿
- 融资集中度：XX%

**操作风险**
- 异常交易：XX 次
- 系统故障：XX 次
- 合规事件：XX 起

## 三、风险趋势

**指标变化**：
| 指标 | 今日 | 昨日 | 变化 |
|-----|------|------|------|
| VaR | XX | XX | XX% |
| 维保比例 | XX% | XX% | XX% |
| LCR | XX% | XX% | XX% |

**趋势判断**：xxx

## 四、预警事项

**当前预警**：
1. XXX（等级：XX）
2. XXX（等级：XX）

**处置进展**：
1. XXX：进行中
2. XXX：已完成
```

### 模板 C：汇报版
> 适用："管理层汇报""决策建议"

```
**风控管理汇报材料** | YYYY-MM-DD

**核心结论**：综合风险指数 XX，整体风险 [可控/需关注/较高]

**关键指标一览**：

| 指标 | 当前值 | 阈值 | 状态 | 趋势 |
|-----|-------|------|------|------|
| 综合风险 | XX | 60 | 🟢 | ↓ |
| VaR | XX 万 | XX 万 | 🟢 | → |
| 维保比例 | XX% | 150% | 🟡 | ↓ |
| LCR | XX% | 120% | 🟢 | → |

**重大风险事项**：
1. XXX（影响：XX，处置：XX）
2. XXX（影响：XX，处置：XX）

**需决策事项**：
1. XXX（建议：XXX）
2. XXX（建议：XXX）

**风险展望**：
- 短期（1 周）：xxx
- 中期（1 月）：xxx

**建议措施**：
1. xxx
2. xxx
```

---

## 特殊情况处理

**数据延迟**：如部分指标数据延迟，说明"XXX 指标数据延迟，暂用最新可用数据"

**指标异常**：如个别指标异常波动，说明"XXX 指标异常，正在核实原因"

**系统故障**：如监控系统故障，说明"监控系统部分功能受限，人工补充数据"

**重大事件**：如发生重大风险事件，说明"已启动应急预案，详见专项报告"

---

## 语言要求

- 先给结论，再给支撑数据
- 风险等级判断要有依据
- 明确区分：指标数据 vs 风险分析 vs 决策建议
- 关键数字、阈值、状态标识单独指出
- 管理层汇报要简洁、重点突出

---

## Reference

**监管要求：**
- 《证券公司风险控制指标管理办法》
- 《证券公司全面风险管理规范》
- 《证券公司流动性风险管理指引》

**指标标准：**
- 净资本/风险覆盖率≥100%
- 流动性覆盖率≥100%
- 净稳定资金率≥100%

**行业实践：**
- 券商风控驾驶舱设计
- 风险管理仪表盘最佳实践
- 管理层风险汇报模板

---

## Scripts

**Python 驾驶舱指标汇总示例：**
```python
import pandas as pd
import numpy as np
from datetime import datetime

def calc_composite_risk_index(risk_scores, weights=None):
    """
    计算综合风险指数
    
    参数:
        risk_scores: 各模块风险分数字典
        weights: 权重字典
    
    返回:
        综合风险指数
    """
    if weights is None:
        weights = {
            'market': 0.3,
            'credit': 0.25,
            'liquidity': 0.25,
            'operational': 0.2
        }
    
    total = 0
    for module, score in risk_scores.items():
        total += score * weights.get(module, 0.25)
    
    return total

def get_risk_level(index):
    """
    获取风险等级
    
    参数:
        index: 风险指数
    
    返回:
        等级标识
    """
    if index > 80:
        return '红色', '🔴'
    elif index > 60:
        return '橙色', '🟠'
    elif index > 40:
        return '黄色', '🟡'
    else:
        return '绿色', '🟢'

def generate_cockpit_summary(risk_data):
    """
    生成驾驶舱摘要
    
    参数:
        risk_data: 风险数据字典
    
    返回:
        摘要字典
    """
    # 计算各模块风险分数
    module_scores = {
        'market': calculate_market_risk(risk_data.get('market', {})),
        'credit': calculate_credit_risk(risk_data.get('credit', {})),
        'liquidity': calculate_liquidity_risk(risk_data.get('liquidity', {})),
        'operational': calculate_operational_risk(risk_data.get('operational', {}))
    }
    
    # 综合风险指数
    composite_index = calc_composite_risk_index(module_scores)
    risk_level, emoji = get_risk_level(composite_index)
    
    summary = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'composite_index': composite_index,
        'risk_level': risk_level,
        'emoji': emoji,
        'module_scores': module_scores,
        'key_metrics': extract_key_metrics(risk_data),
        'alerts': extract_alerts(risk_data)
    }
    
    return summary

def calculate_market_risk(data):
    """计算市场风险分数"""
    var_ratio = data.get('var_ratio', 0)  # VaR/限额
    stress_loss = data.get('stress_loss_ratio', 0)
    concentration = data.get('concentration', 0)
    
    score = var_ratio * 40 + stress_loss * 30 + concentration * 30
    return min(score, 100)

def calculate_credit_risk(data):
    """计算信用风险分数"""
    margin_ratio = data.get('avg_maintenance_ratio', 200)
    warning_accounts = data.get('warning_accounts', 0)
    liquidation_accounts = data.get('liquidation_accounts', 0)
    
    ratio_score = max(0, (200 - margin_ratio) / 50 * 40)
    warning_score = min(warning_accounts / 10 * 30, 30)
    liquidation_score = min(liquidation_accounts / 5 * 30, 30)
    
    return min(ratio_score + warning_score + liquidation_score, 100)

def calculate_liquidity_risk(data):
    """计算流动性风险分数"""
    lcr = data.get('lcr', 150)
    nsfr = data.get('nsfr', 150)
    funding_gap = data.get('funding_gap_ratio', 0)
    
    lcr_score = max(0, (150 - lcr) / 50 * 40)
    nsfr_score = max(0, (150 - nsfr) / 50 * 30)
    gap_score = min(funding_gap / 10 * 30, 30)
    
    return min(lcr_score + nsfr_score + gap_score, 100)

def calculate_operational_risk(data):
    """计算操作风险分数"""
    abnormal_trades = data.get('abnormal_trades', 0)
    system_failures = data.get('system_failures', 0)
    compliance_events = data.get('compliance_events', 0)
    
    trade_score = min(abnormal_trades / 20 * 40, 40)
    failure_score = min(system_failures / 5 * 30, 30)
    compliance_score = min(compliance_events / 3 * 30, 30)
    
    return min(trade_score + failure_score + compliance_score, 100)

def extract_key_metrics(risk_data):
    """提取关键指标"""
    return {
        'var': risk_data.get('market', {}).get('var', 0),
        'maintenance_ratio': risk_data.get('credit', {}).get('avg_maintenance_ratio', 0),
        'lcr': risk_data.get('liquidity', {}).get('lcr', 0),
        'abnormal_trades': risk_data.get('operational', {}).get('abnormal_trades', 0)
    }

def extract_alerts(risk_data):
    """提取预警事项"""
    alerts = []
    if risk_data.get('credit', {}).get('avg_maintenance_ratio', 200) < 150:
        alerts.append('维保比例低于预警线')
    if risk_data.get('operational', {}).get('abnormal_trades', 0) > 10:
        alerts.append('异常交易频发')
    return alerts
```

**SQL 查询示例：**
```sql
-- 查询风控驾驶舱核心指标
SELECT 
    '市场风险' as module,
    var_value as key_metric1,
    var_limit as key_metric2,
    var_value / var_limit * 100 as usage_ratio,
    stress_test_loss as key_metric3
FROM market_risk WHERE date = CURDATE()
UNION ALL
SELECT 
    '信用风险',
    avg_maintenance_ratio,
    warning_account_count,
    liquidation_account_count,
    margin_balance
FROM credit_risk WHERE date = CURDATE()
UNION ALL
SELECT 
    '流动性风险',
    lcr,
    nsfr,
    funding_gap,
    cash_reserve
FROM liquidity_risk WHERE date = CURDATE()
UNION ALL
SELECT 
    '操作风险',
    abnormal_trade_count,
    system_failure_count,
    compliance_event_count,
    NULL
FROM operational_risk WHERE date = CURDATE();
```
