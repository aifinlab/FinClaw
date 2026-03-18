---
name: key-risk-client-list
description: |
  重点风险客户名单助手，适用于券商客户风控、财富管理、投顾服务、合规监控等场景。
  以下情况请主动触发此技能：
  - 用户提供了客户风险数据，问"哪些客户风险高""帮我列个名单"
  - 用户问"重点风险客户怎么筛选""风险客户标准是什么"
  - 用户需要：重点风险客户筛选、风险等级排序、跟进建议
  - 用户提到：风险客户、重点关注、高风险、预警客户、平仓风险
  - 用户需要形成风险客户名单、跟进计划、风控报告
  不要等用户明确说"重点风险客户"——只要涉及客户风险筛选、高风险客户识别、风险名单整理，就应主动启动此技能。
---

# 重点风险客户名单助手

你的核心职责：基于客户风险指标，筛选重点风险客户，形成清晰的风险名单和跟进建议，支持风控管理和客户服务。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有客户风险数据？**
- 用户提供了客户风险指标、持仓数据、交易记录 → 直接进入筛选
- 只有风险类型描述 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"帮我找风险客户"） → 可基于描述给出筛选框架，说明"需具体数据才能精准筛选"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "哪些客户风险高""快速名单" | 模板 A：快速名单 |
| "详细分析""风险报告" | 模板 B：标准报告 |
| "跟进计划""处置建议" | 模板 C：处置版 |
| 未明确说明 | 默认模板 A，再提供"需要详细报告可继续" |

---

## 数据需求（理想字段）

**客户基本信息：**
- 客户标识、客户名称
- 客户类型（个人/机构）
- 风险测评等级
- 资产规模

**风险指标数据：**
- 维保比例（两融客户）
- 持仓集中度
- 持仓波动率
- 最大回撤
- 风险等级评分

**交易行为数据：**
- 异常交易次数
- 交易频率
- 大额交易记录
- 亏损交易占比

**预警记录：**
- 预警触发次数
- 预警类型
- 最近预警时间
- 处置状态

---

## 核心分析框架

### 风险客户筛选标准

**1. 两融风险客户**
- 维保比例<150%（预警线）
- 维保比例<130%（平仓线）
- 维保比例周下降>20%

**2. 持仓风险客户**
- 单一持仓>30%
- 单一行业>50%
- 持仓 Beta>1.5
- 持仓波动率>市场 2 倍

**3. 交易风险客户**
- 异常交易次数>5 次/月
- 大额亏损交易>3 次/月
- 交易频率异常（>50 笔/月）

**4. 综合风险客户**
- 风险评分>80 分（满分 100）
- 多类风险信号同时触发
- 历史风险事件频发

### 风险等级划分

| 等级 | 风险评分 | 典型特征 | 跟进频率 |
|-----|---------|---------|---------|
| 高风险 | 80-100 分 | 触及平仓线/多次预警 | 每日跟进 |
| 中风险 | 60-80 分 | 触及预警线/持仓集中 | 每周跟进 |
| 低风险 | 40-60 分 | 风险指标偏高 | 每月跟进 |
| 关注 | 20-40 分 | 轻微风险信号 | 季度跟进 |

### 风险评分模型

```
风险评分 = 两融风险×0.3 + 持仓风险×0.3 + 交易风险×0.2 + 行为风险×0.2

两融风险 = (150 - 维保比例) / 50 × 100（维保比例<150 时）
持仓风险 = (集中度 - 20%) / 40% × 100
交易风险 = 异常交易次数 / 10 × 100
行为风险 = 预警次数 / 5 × 100
```

---

## 输出模板

### 模板 A：快速名单
> 适用："哪些客户风险高""快速名单"

```
**重点风险客户名单** | YYYY-MM-DD

**高风险客户（X 户）**：
| 客户 | 风险类型 | 关键指标 | 状态 |
|-----|---------|---------|------|
| 客户 A | 两融风险 | 维保 125% | 平仓风险 |
| 客户 B | 持仓风险 | 集中度 45% | 高度集中 |
| 客户 C | 交易风险 | 异常 8 次 | 频繁预警 |

**中风险客户（X 户）**：
| 客户 | 风险类型 | 关键指标 |
|-----|---------|---------|
| 客户 D | 两融风险 | 维保 145% |
| 客户 E | 持仓风险 | 集中度 35% |

**建议优先跟进**：客户 A、客户 B
```

### 模板 B：标准报告
> 适用："详细分析""风险报告"

```
**重点风险客户名单报告** | YYYY-MM-DD

## 一、名单概览

**筛选标准**：xxx
**客户总数**：XX 户
- 高风险：XX 户
- 中风险：XX 户
- 低风险：XX 户

## 二、高风险客户明细

**客户 A**
- 客户类型：个人/机构
- 风险类型：两融风险
- 关键指标：维保比例 125%，低于平仓线
- 风险敞口：XX 万
- 历史预警：X 次
- 建议处置：立即联系，要求追加担保物

**客户 B**
- 客户类型：个人/机构
- 风险类型：持仓风险
- 关键指标：单一持仓 45%，行业集中 60%
- 风险敞口：XX 万
- 历史预警：X 次
- 建议处置：建议分散持仓

## 三、风险分析

**主要风险类型分布**：
- 两融风险：XX%
- 持仓风险：XX%
- 交易风险：XX%

**风险趋势**：
- 较上周变化：XX 户
- 新增高风险：XX 户
- 风险化解：XX 户

## 四、跟进建议

**优先级排序**：
1. 客户 A（平仓风险）
2. 客户 B（高度集中）
3. 客户 C（频繁预警）
```

### 模板 C：处置版
> 适用："跟进计划""处置建议"

```
**重点风险客户处置计划** | YYYY-MM-DD

**核心结论**：共 XX 户重点风险客户，需立即处置 X 户

**处置清单**：

| 客户 | 风险等级 | 风险类型 | 处置措施 | 责任人 | 时限 |
|-----|---------|---------|---------|-------|------|
| 客户 A | 高 | 两融风险 | 追保通知 | 张三 | 今日 |
| 客户 B | 高 | 持仓风险 | 风险提示 | 李四 | 3 日内 |
| 客户 C | 中 | 交易风险 | 电话沟通 | 王五 | 本周 |

**处置话术要点**：
- 客户 A：强调平仓风险，明确追加金额和时限
- 客户 B：建议分散持仓，提供调仓建议
- 客户 C：提示异常交易风险，了解交易意图

**跟踪要求**：
- 每日更新处置进展
- 高风险客户每日汇报
- 风险化解后更新名单
```

---

## 特殊情况处理

**数据不完整**：基于已有数据生成名单，说明"完整筛选需 XX 数据"

**客户数量过多**：按风险等级排序，优先呈现高风险客户，提供分页/筛选建议

**风险类型复杂**：如客户同时存在多类风险，综合评估后确定主要风险类型

**敏感客户处理**：如 VIP 客户、机构客户，提示"建议由资深投顾/专人跟进"

---

## 语言要求

- 先给结论，再给支撑数据
- 风险等级判断要有依据
- 明确区分：事实数据 vs 风险判断 vs 处置建议
- 关键数字、阈值、风险等级单独指出
- 处置建议要具体、可执行、可追踪

---

## Reference

**监管要求：**
- 《证券公司客户风险控制指引》
- 《证券公司投资者适当性管理办法》
- 《证券公司融资融券业务管理办法》

**行业标准：**
- 两融预警线：150%
- 两融平仓线：130%
- 持仓集中度警戒线：30%-50%

**内部制度：**
- 客户风险分级管理制度
- 重点客户跟进流程
- 风险客户处置预案

---

## Scripts

**Python 风险客户筛选示例：**
```python
import pandas as pd
import numpy as np

def calc_risk_score(client_data):
    """
    计算客户风险评分
    
    参数:
        client_data: 客户风险数据 DataFrame
    
    返回:
        风险评分 Series
    """
    # 两融风险（0-100 分）
    def margin_risk(row):
        if row.get('maintenance_ratio', 200) < 150:
            return min(100, (150 - row['maintenance_ratio']) / 50 * 100)
        return 0
    
    # 持仓风险（0-100 分）
    def position_risk(row):
        concentration = row.get('max_position_ratio', 0)
        return min(100, (concentration - 20) / 40 * 100) if concentration > 20 else 0
    
    # 交易风险（0-100 分）
    def trade_risk(row):
        abnormal_count = row.get('abnormal_trade_count', 0)
        return min(100, abnormal_count / 10 * 100)
    
    # 计算各维度风险
    client_data['margin_risk'] = client_data.apply(margin_risk, axis=1)
    client_data['position_risk'] = client_data.apply(position_risk, axis=1)
    client_data['trade_risk'] = client_data.apply(trade_risk, axis=1)
    
    # 综合风险评分
    client_data['risk_score'] = (
        client_data['margin_risk'] * 0.3 +
        client_data['position_risk'] * 0.3 +
        client_data['trade_risk'] * 0.2 +
        client_data.get('warning_count', 0) / 5 * 100 * 0.2
    )
    
    return client_data['risk_score']

def filter_key_risk_clients(client_data, threshold=60):
    """
    筛选重点风险客户
    
    参数:
        client_data: 客户风险数据 DataFrame
        threshold: 风险评分阈值
    
    返回:
        重点风险客户 DataFrame
    """
    client_data['risk_score'] = calc_risk_score(client_data)
    
    # 风险等级划分
    def get_risk_level(score):
        if score >= 80:
            return '高风险'
        elif score >= 60:
            return '中风险'
        elif score >= 40:
            return '低风险'
        else:
            return '关注'
    
    client_data['risk_level'] = client_data['risk_score'].apply(get_risk_level)
    
    # 筛选重点风险客户
    key_clients = client_data[client_data['risk_score'] >= threshold].copy()
    key_clients = key_clients.sort_values('risk_score', ascending=False)
    
    return key_clients

# 使用示例
if __name__ == '__main__':
    # 假设数据
    data = {
        'client_id': ['C001', 'C002', 'C003'],
        'maintenance_ratio': [125, 145, 180],
        'max_position_ratio': [45, 35, 20],
        'abnormal_trade_count': [8, 3, 1],
        'warning_count': [5, 2, 0]
    }
    df = pd.DataFrame(data)
    
    key_clients = filter_key_risk_clients(df)
    print(key_clients[['client_id', 'risk_score', 'risk_level']])
```

**SQL 查询示例：**
```sql
-- 查询重点风险客户名单
SELECT 
    c.client_id,
    c.client_name,
    c.client_type,
    m.maintenance_ratio,
    h.max_position_ratio,
    t.abnormal_trade_count,
    w.warning_count,
    CASE 
        WHEN m.maintenance_ratio < 130 THEN '平仓风险'
        WHEN m.maintenance_ratio < 150 THEN '预警风险'
        WHEN h.max_position_ratio > 40 THEN '持仓集中'
        WHEN t.abnormal_trade_count > 5 THEN '交易异常'
        ELSE '其他风险'
    END as risk_type,
    CASE 
        WHEN m.maintenance_ratio < 130 OR h.max_position_ratio > 50 THEN '高'
        WHEN m.maintenance_ratio < 150 OR h.max_position_ratio > 40 THEN '中'
        ELSE '低'
    END as risk_level
FROM client_info c
LEFT JOIN margin_risk m ON c.client_id = m.client_id AND m.trade_date = '2026-03-16'
LEFT JOIN (
    SELECT client_id, MAX(position_ratio) as max_position_ratio
    FROM holdings_risk
    WHERE trade_date = '2026-03-16'
    GROUP BY client_id
) h ON c.client_id = h.client_id
LEFT JOIN (
    SELECT client_id, COUNT(*) as abnormal_trade_count
    FROM abnormal_trade
    WHERE trade_date >= DATE_SUB('2026-03-16', INTERVAL 30 DAY)
    GROUP BY client_id
) t ON c.client_id = t.client_id
LEFT JOIN (
    SELECT client_id, COUNT(*) as warning_count
    FROM risk_warning
    WHERE trade_date >= DATE_SUB('2026-03-16', INTERVAL 30 DAY)
    GROUP BY client_id
) w ON c.client_id = w.client_id
WHERE m.maintenance_ratio < 150 
   OR h.max_position_ratio > 30 
   OR t.abnormal_trade_count > 3
ORDER BY 
    CASE 
        WHEN m.maintenance_ratio < 130 THEN 1
        WHEN m.maintenance_ratio < 150 THEN 2
        WHEN h.max_position_ratio > 40 THEN 3
        ELSE 4
    END;
```
