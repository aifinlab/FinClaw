---
name: a-share-thematic-invest
description: A股主题投资/赛道分析。当用户说"主题投资"、"赛道"、"风口"、"thematic"、"XX赛道怎么样"、"AI投资机会"、"新能源赛道"、"半导体赛道"、"医药赛道"、"国产替代"、"数字经济"、"新质生产力"时触发。深度分析特定投资主题/赛道的产业逻辑、市场空间、竞争格局、估值水平和核心标的，评估主题的持续性和投资时机。支持研报风格（formal）和快速分析风格（brief）。
---

# A股主题投资/赛道分析

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 概念板块列表（akshare，获取主题相关概念板块）
python -c "import akshare as ak; df=ak.stock_board_concept_name_em(); print(df.to_json(orient='records', force_ascii=False))"

# 概念板块成分股（akshare，需指定板块名称）
python -c "import akshare as ak; df=ak.stock_board_concept_cons_em(symbol='人工智能'); print(df.to_json(orient='records', force_ascii=False))"

# 核心标的实时行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],...

# 核心标的K线（判断趋势）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]

# 核心标的财务数据（估值/业绩弹性）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE1],[CODE2],...

# 核心标的资金流向
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE]
```

补充：通过 web 搜索获取产业政策、市场空间/TAM数据、渗透率、技术进展、研报观点。

## Workflow

1. **定义主题**：明确投资主题的核心逻辑
   - 产业逻辑：技术突破 / 需求爆发 / 供给侧变革
   - 政策驱动：国家战略 / 产业政策 / 补贴扶持
   - 事件催化：技术里程碑 / 标志性订单 / 海外映射
   - 搜索最新政策文件、产业新闻，确认主题时效性

2. **市场空间测算**：量化赛道规模
   - TAM（总可寻址市场）/ SAM（可服务市场）/ SOM（可获得市场）
   - 当前渗透率 → 判断增长曲线位置（S曲线：0-10%萌芽, 10-30%加速, 30-50%快速普及, 50%+成熟）
   - 未来3-5年CAGR预测
   - 与海外对标（中美差距 / 国产替代空间）

3. **核心标的梳理**：绘制主题投资地图
   - 通过概念板块获取相关个股列表
   - 按产业链环节分层：上游（材料/设备）→ 中游（制造/集成）→ 下游（应用/场景）
   - 每个环节筛选核心标的，获取：市值、PE/PB、营收增速、归母净利增速、毛利率
   - 业绩弹性评估：主题相关收入占比、边际改善空间

4. **主题时机研判**：评估当前阶段
   - 主题生命周期：萌芽期（认知差大）→ 加速期（业绩兑现）→ 成熟期（估值消化）→ 衰退期（逻辑证伪/边际递减）
   - 估值水平：板块整体PE/PB分位数，与历史对比
   - 资金面：机构持仓变化、北向资金动向、融资余额
   - 拥挤度：换手率、关注度、卖方覆盖密度

5. **输出**：按用户偏好输出
   - **formal**（研报风格）：完整的主题投资报告，含市场空间、竞争格局、核心标的、投资建议
   - **brief**（快速分析，默认）：赛道核心逻辑 + 关键数据 + 核心标的 + 风险提示

## 关键规则

1. **区分概念炒作和真正产业趋势**：有业绩兑现路径的才是好赛道，纯故事的是炒作
2. **关注渗透率判断所处阶段**：渗透率10-30%是最佳投资窗口，50%以上增速放缓
3. **主题不等于买最贵的龙头**：产业链中利润最厚的环节 ≠ 市值最大的公司，关注"卡位"价值
4. **政策持续性很重要**：一次性政策利好 vs 长期战略支持，决定主题持续时间
5. **警惕主题过热信号**：全市场讨论、卖方集中推荐、散户大量涌入、估值严重脱离基本面

## 参考资料

- [主题投资分析指南](references/thematic-invest-guide.md)
