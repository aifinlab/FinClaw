# 输入字段口径

## 基本信息
- `client_profile`
  - `client_id`：客户编号（可选）
  - `name`：客户姓名/称谓
  - `age`：年龄
  - `risk_level`：风险等级（1-5 或 保守/稳健/平衡/进取）
  - `investment_horizon_months`：计划持有期（月）
  - `liquidity_need`：流动性需求（高/中/低）
  - `goals`：主要目标（现金流、稳健增值、养老、子女教育等）
  - `communication_preference`：沟通偏好

## 赎回请求
- `redemption_request`
  - `requested_amount`：赎回金额
  - `requested_ratio`：赎回比例
  - `urgency`：紧急程度（高/中/低）
  - `reason`：赎回原因（现金需求/亏损/听闻负面等）
  - `channel`：触达渠道（电话/面谈/线上）
  - `cash_need_date`：资金需求日期（可选）

## 持仓信息
- `holdings`（列表）
  - `product_id`：产品编号
  - `name`：产品名称
  - `asset_class`：资产类别
  - `risk_level`：产品风险等级
  - `purchase_date`：购买日期
  - `min_holding_months`：最短持有期
  - `lockup_months`：封闭期
  - `market_value`：当前市值
  - `unrealized_return_pct`：浮动盈亏（%）
  - `liquidity`：流动性描述
  - `fees`：赎回费/管理费说明
  - `recent_events`：产品相关事件/公告

## 市场与合规
- `market_context`
  - `volatility_level`：波动水平（高/中/低）
  - `rate_trend`：利率趋势
  - `policy_notes`：政策/行业事件
  - `headline_risks`：市场风险摘要
- `compliance_constraints`
  - `forbidden_phrases`：禁用表述清单
  - `must_disclose`：必须披露要点

## 输出偏好
- `output`
  - `format`：`markdown` 或 `json`
