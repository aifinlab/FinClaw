# 输入字段规范（建议）

## 基础信息
- `client_profile`
  - `name`：客户称呼（可匿名）
  - `segment`：客户类型（大众/高净值/私行/机构）
  - `risk_level`：风险等级（R1-R5 或保守/稳健/平衡/进取）
  - `horizon`：资金期限偏好（短/中/长）
  - `liquidity_need`：流动性要求（高/中/低）
  - `communication_style`：沟通偏好（数据型/情感型/简短/深入）

## 持仓与产品
- `holdings_summary`
  - `products`：产品列表
    - `name`
    - `type`（固收/混合/权益/另类/现金管理）
    - `risk_level`
    - `allocation_pct`
    - `unrealized_return_pct`（近阶段浮盈亏）
  - `total_drawdown_pct`：组合阶段回撤（如可用）
  - `concentration_notes`：集中度提示

## 市场与事件
- `market_context`
  - `event`：触发事件
  - `drivers`：主要驱动因素
  - `volatility_level`：波动水平（低/中/高）
  - `data_points`：可引用的事实/数据（非预测）

## 沟通场景
- `touchpoint`
  - `channel`：电话/面谈/微信/短信/邮件
  - `objective`：安抚/解释/留存/再平衡评估
  - `emotion_state`：焦虑/疑惑/愤怒/观望
  - `constraints`：禁用表述与合规要求

## 需要补充的关键字段（缺失时要提示）
- 产品风险等级与适当性匹配
- 持仓占比与波动来源
- 客户期限与资金用途
- 近期市场事实与可验证信息
