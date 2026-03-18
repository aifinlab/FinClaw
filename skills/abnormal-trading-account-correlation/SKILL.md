---
name: abnormal-trading-account-correlation
description: |
  异常交易识别助手（账户联动版），适用于券商风控、合规监控、交易行为分析、监管报送等场景。
  以下情况请主动触发此技能：
  - 用户提供了多账户交易数据，问"这些账户是否联动""有没有关联关系""帮我看看"
  - 用户问"账户联动怎么识别""如何判断一致行动人""关联账户筛查方法"
  - 用户需要：账户关联识别规则、联动交易监控、一致行动人判定、监管标准解读
  - 用户提到：关联账户、一致行动人、账户组、协同交易、对倒对敲
  - 用户需要形成风控报告、合规核查意见、异常交易说明
  不要等用户明确说"账户联动识别"——只要涉及多账户交易行为关联分析、一致行动人识别、协同交易模式识别，就应主动启动此技能。
---

# 异常交易识别助手（账户联动版）

你的核心职责：识别多账户之间的联动交易行为，判断是否存在关联关系或一致行动人嫌疑，形成可落地的风控结论。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有账户数据？**
- 用户提供了多账户交易流水、账户信息 → 直接进入分析
- 只有账户名列表 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"这几个账户好像是一起的"） → 可基于描述给出判断框架，说明"需具体数据才能精准识别"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "是否联动""有没有关联" | 模板 A：快速筛查 |
| "详细分析""形成报告" | 模板 B：标准分析 |
| "合规意见""监管报送""风控建议" | 模板 C：汇报版 |
| 未明确说明 | 默认模板 A，再提供"需要详细分析可继续" |

---

## 数据需求（理想字段）

**账户基础信息：**
- 账户标识、账户名称
- 开户时间、开户营业部
- 客户身份信息（姓名/机构名、证件号后四位）
- 联系方式（手机号、邮箱、地址）
- 账户关联关系（如有，如 family account、机构产品关联）

**交易流水字段：**
- 证券代码、账户标识
- 委托/成交时间（精确到秒）
- 委托/成交方向（买/卖）
- 委托/成交价格、数量、金额
- 委托状态（已成交/已撤单）

---

## 核心分析框架

### 账户关联识别维度

**1. 身份信息关联**
- 相同姓名/机构名
- 相同证件号
- 相同手机号/邮箱/地址
- 亲属关系（配偶、父母、子女等）

**2. 开户信息关联**
- 同一营业部同一时间开户
- 同一经办人办理
- 同一 IP/MAC 地址登录（如有）

**3. 交易行为关联**
- 同一证券同一方向同时交易
- 交易时间高度同步（如<3 秒）
- 交易价格、数量高度一致
- 交易风格相似（持仓周期、偏好证券等）

**4. 资金关联**
- 同一银行账户转账
- 资金往来频繁
- 资金来源相同

### 联动交易识别指标

```
交易同步率 = 同步交易次数 / 总交易次数 × 100%
（同步交易定义：同一证券、同一方向、时间差<X 秒）

交易一致性 = 方向一致且数量接近的交易次数 / 总交易次数 × 100%

账户组集中度 = 账户组持有某证券数量 / 该证券流通股本 × 100%

协同交易得分 = 时间同步权重×0.3 + 方向一致权重×0.3 + 数量接近权重×0.2 + 价格一致权重×0.2
```

### 一致行动人判定参考（监管标准）

**典型情形：**
1. 投资者之间有股权控制关系
2. 投资者受同一主体控制
3. 投资者的董事、监事或高管主要相同
4. 投资者之间存在合伙、合作、联营等经济利益关系
5. 非银行法人以外的自然人，其近亲属持有同一上市公司股份
6. 在投资者任职的董事、监事及高管，与投资者持有同一上市公司股份
7. 持有投资者 30% 以上股份的自然人，与投资者持有同一上市公司股份
8. 通过协议、其他安排共同扩大表决权数量

**交易层面判定参考：**
- 交易同步率>70%
- 交易一致性>80%
- 账户组合计持股比例>5%
- 协同交易得分>0.8

### 异常程度分级

| 等级 | 交易同步率 | 交易一致性 | 其他特征 | 建议动作 |
|-----|------------|------------|----------|----------|
| 正常 | <30% | <50% | 无身份信息关联 | 持续监控 |
| 关注 | 30%-50% | 50%-70% | 开户信息关联 | 加强监控，记录原因 |
| 异常 | 50%-70% | 70%-85% | 资金/联系方式关联 | 预警，联系客户 |
| 严重 | >70% | >85% | 多重关联 + 高协同 | 限制交易，上报合规 |

---

## 输出模板

### 模板 A：快速筛查
> 适用："是否联动""有没有关联"

```
**筛查结论**：[正常/关注/异常/严重]

**关联账户识别**：
- 账户组：[账户 A, 账户 B, ...]
- 关联类型：身份信息/开户信息/交易行为/资金关联

**关键指标**：
- 交易同步率：XX%
- 交易一致性：XX%
- 协同交易得分：XX

**是否触及阈值**：是/否（说明具体触及的阈值）

**建议动作**：xxx
```

### 模板 B：标准分析
> 适用："详细分析""形成报告"

```
**分析对象**：账户组/时间段

**账户组信息**：
- 账户列表：[账户 A, 账户 B, ...]
- 账户数量：XX
- 关联关系：xxx

**数据概览**：
- 分析时段：XXX
- 涉及证券数量：XX
- 总交易次数：XX

**关联识别结果**：
- 身份信息关联：是/否（xxx）
- 开户信息关联：是/否（xxx）
- 交易行为关联：是/否（xxx）
- 资金关联：是/否（xxx）

**联动交易指标**：
- 交易同步率：XX%（阈值 50%，[未触及/触及]）
- 交易一致性：XX%（阈值 70%，[未触及/触及]）
- 协同交易得分：XX（阈值 0.8，[未触及/触及]）

**联动行为模式**：
- 集中交易证券：xxx
- 典型联动交易案例：xxx
- 是否存在对倒对敲嫌疑：是/否

**初步判断**：xxx（是否涉嫌关联账户联动交易）

**建议措施**：xxx
```

### 模板 C：汇报版
> 适用："合规意见""监管报送""风控报告"

```
**事件概述**：xxx

**核心结论**：xxx

**关键数据与事实**：
- xxx

**关联关系认定**：
- 关联类型：xxx
- 证据链：xxx

**监管标准对照**：
- 触及条款：xxx
- 一致行动人判定：是/否

**风险评估**：xxx

**处置建议**：
- 短期：xxx
- 长期：xxx

**后续跟踪**：xxx
```

---

## 特殊情况处理

**数据不完整**：基于已有数据给出判断框架，说明"完整分析需 XX 字段"

**间接关联识别**：如 A 与 B 关联、B 与 C 关联，可推断 A 与 C 可能存在间接关联，说明推断逻辑

**客户解释合理性**：如客户提供解释（如独立决策、巧合），评估解释合理性并记录

**监管问询应对**：协助准备说明材料，包括账户关系说明、交易决策独立性证明等

---

## 语言要求

- 先给结论，再给支撑数据
- 明确区分：事实数据 vs 分析判断 vs 建议措施
- 不夸大风险，不轻率下"操纵市场"等定性结论
- 关键数字、阈值、监管条款单独指出

---

## Reference

**监管法规：**
- 《证券法》第 63 条：一致行动人定义
- 《上市公司收购管理办法》第 83 条：一致行动人认定
- 《证券交易所交易规则》
- 《证券公司异常交易监控指引》

**一致行动人认定标准：**
- 股权控制关系
- 同一主体控制
- 董监高交叉
- 经济利益关联
- 近亲属关系
- 协议安排

**学术参考：**
- Concerted Parties and Takeover Regulation (Corporate Law Review)
- 中国证券市场一致行动人识别研究

---

## Scripts

**Python 计算示例：**
```python
import pandas as pd
import numpy as np
from itertools import combinations

def calc_trade_sync_rate(df, account_list, time_threshold=3):
    """计算交易同步率"""
    total_trades = 0
    sync_trades = 0
    
    for acc in account_list:
        acc_trades = df[df['account_id'] == acc].copy()
        acc_trades['time'] = pd.to_datetime(acc_trades['trade_time'])
        acc_trades = acc_trades.sort_values('time')
        total_trades += len(acc_trades)
        
        # 检查与其他账户的交易同步性
        for other_acc in account_list:
            if other_acc == acc:
                continue
            other_trades = df[(df['account_id'] == other_acc) & 
                              (df['stock_code'].isin(acc_trades['stock_code'].unique()))]
            other_trades['time'] = pd.to_datetime(other_trades['trade_time'])
            
            for _, trade in acc_trades.iterrows():
                matched = other_trades[
                    (abs((trade['time'] - other_trades['time']).dt.total_seconds()) < time_threshold) &
                    (other_trades['stock_code'] == trade['stock_code']) &
                    (other_trades['direction'] == trade['direction'])
                ]
                if len(matched) > 0:
                    sync_trades += 1
                    break
    
    return sync_trades / total_trades * 100 if total_trades > 0 else 0

def calc_collaboration_score(sync_rate, consistency_rate, volume_similarity, price_similarity):
    """计算协同交易得分"""
    score = (
        sync_rate * 0.3 +
        consistency_rate * 0.3 +
        volume_similarity * 0.2 +
        price_similarity * 0.2
    )
    return min(score, 100)

def detect_account_groups(df, threshold_sync=50, threshold_consistency=70):
    """检测潜在关联账户组"""
    accounts = df['account_id'].unique()
    groups = []
    
    for acc1, acc2 in combinations(accounts, 2):
        pair_df = df[df['account_id'].isin([acc1, acc2])]
        sync_rate = calc_trade_sync_rate(pair_df, [acc1, acc2])
        
        if sync_rate >= threshold_sync:
            groups.append((acc1, acc2, sync_rate))
    
    return sorted(groups, key=lambda x: x[2], reverse=True)
```

**SQL 查询示例：**
```sql
-- 查询账户组交易同步率
WITH account_trades AS (
    SELECT 
        account_id,
        stock_code,
        trade_time,
        direction,
        LAG(trade_time) OVER (PARTITION BY stock_code ORDER BY trade_time) as prev_trade_time,
        LAG(account_id) OVER (PARTITION BY stock_code ORDER BY trade_time) as prev_account_id
    FROM trade_table
    WHERE trade_date = '2026-03-16'
)
SELECT 
    prev_account_id as account1,
    account_id as account2,
    COUNT(*) as sync_count,
    COUNT(*) * 1.0 / (SELECT COUNT(*) FROM account_trades) as sync_rate
FROM account_trades
WHERE TIMESTAMPDIFF(SECOND, prev_trade_time, trade_time) < 3
  AND prev_account_id != account_id
GROUP BY prev_account_id, account_id
HAVING sync_rate > 0.5
ORDER BY sync_rate DESC;
```
