# 输入结构说明（产品卖点生成）

## 基本说明

- 本输入用于生成“产品卖点包 + 适配理由 + 风险提示 + 异议处理 + 跟进清单”。
- 字段可缺省，但若缺失核心字段，将在输出中提示信息缺口。

## 顶层字段

- `request_id`：请求编号（可选）
- `client_profile`：客户画像
- `product`：单只产品信息（卖点核心）
- `product_pool`：可选产品池（用于对比与备选方案）
- `market_view`：市场观点或宏观环境
- `selling_context`：沟通场景与本次目标
- `constraints`：渠道、合规、适当性或其他限制

## client_profile（客户画像）

- `name`：客户名称或编号
- `age`：年龄（可选）
- `risk_level`：风险等级（如“稳健/平衡/进取”或 1-5）
- `investment_horizon_months`：投资期限（月）
- `liquidity_need`：流动性需求（高/中/低）
- `goals`：目标清单（数组）
- `constraints`：客户约束（数组，如“不可接受浮亏”）
- `current_holdings`：当前持仓摘要（可选）
- `experience_level`：投资经验（低/中/高）
- `communication_preference`：沟通偏好（短/详细/可视化）

## product（单只产品）

- `product_id`：产品编号
- `name`：产品名称
- `asset_class`：资产类别（固收/权益/混合/另类等）
- `risk_level`：产品风险等级
- `strategy`：产品策略或投资范围
- `term_months`：期限（月）
- `liquidity`：流动性说明（如“封闭12个月/按季开放”）
- `min_investment`：起投金额
- `expected_return_range`：预期收益区间（如“3-5%/年”）
- `performance_features`：历史表现特征（如“回撤控制/波动较低”）
- `income_type`：收益类型（如“固定收益/浮动收益”）
- `fee_structure`：费用结构
- `redemption_rules`：赎回规则或费用
- `key_risks`：关键风险（数组）
- `selling_highlights`：产品亮点（数组，可选）
- `suitable_for`：适配客群或场景

## product_pool（可选产品池）

数组结构，每个元素与 `product` 字段一致，用于备选方案生成。

## market_view（市场观点）

- `rate_environment`：利率环境
- `volatility`：市场波动水平
- `trend_summary`：趋势描述
- `policy_notes`：政策/监管提示
- `opportunities`：结构性机会（数组）
- `risks`：宏观风险提示（数组）

## selling_context（沟通场景）

- `channel`：渠道（网点/电话/线上/路演）
- `meeting_goal`：本次目标（如“引导认购/解释波动/续投”）
- `stage`：沟通阶段（首次/复访/跟进）
- `objections`：客户异议或担忧（数组）
- `competitors`：竞品信息（可选）
- `compliance_constraints`：合规约束或提示

## constraints（其他约束）

- `distribution_limits`：渠道或销售限制
- `suitability_rules`：适当性规则
- `material_requirements`：必须披露的信息
