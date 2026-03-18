# 输出结构说明

建议输出 JSON 或 Markdown 时至少包含以下字段：

- task_summary：任务摘要
- customer_profile：客户画像
- constraints：配置约束
- current_portfolio_diagnosis：当前持仓诊断
- market_context：市场与行业数据说明
- primary_plan：主方案
- alternative_plans：备选方案列表
- rebalance_actions：再平衡建议
- risks：风险提示
- information_gaps：信息缺口
- next_steps：后续动作

其中 `primary_plan` 建议包含：
- plan_name
- target_customer
- asset_ranges
- rationale
- key_risks
- suitability_notes
