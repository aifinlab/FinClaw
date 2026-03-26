---
name: a-share-money-flow
description: A股主力资金/大单追踪/资金流向分析。当用户说"主力资金"、"大单"、"资金流向"、"主力在干嘛"、"资金净流入"、"主力买入"、"大资金"、"XX的资金流向"、"主力动向"、"smart money"、"主力资金流入流出"、"资金流向分析"、"大单净买入"、"超大单"、"主力净流入"时触发。MUST USE when user asks about main capital flow, large order tracking, money flow analysis, net inflow/outflow of institutional money, or smart money movement for individual stocks or the overall market. 基于 cn-stock-data 资金流向数据（超大单/大单/中单/小单），分析个股或市场的主力资金行为。支持机构级分析（formal）和快速判断（brief）。与 a-share-northbound 的区别：本 skill 聚焦场内主力资金（大单/超大单），northbound 聚焦北向外资。
---

# A股主力资金/大单追踪分析

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 个股资金流向（含超大单/大单/中单/小单）
python "$SCRIPTS/cn_stock_data.py" fund_flow --code [CODE]

# 个股行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]

# K线（叠加资金流分析）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
```

补充：web 搜索获取全市场资金流向排名（净流入/净流出 Top 20）。

## Workflow

1. **确定分析范围**：个股资金流分析 / 全市场资金排名 / 板块资金对比
2. **数据获取**：资金流向（按单子大小分层）+ 行情数据
3. **资金结构分析**：
   - 超大单（>100万）净流入 → 机构/大户方向
   - 大单（20-100万）净流入 → 中大户方向
   - 中单（4-20万）净流入 → 散户主力
   - 小单（<4万）净流入 → 散户方向
   - **主力净流入 = 超大单 + 大单净流入**
4. **趋势判断**：
   - 连续 N 日主力净流入/流出
   - 资金流与股价走势是否一致（量价背离）
   - 主力净流入占成交额比例
5. **输出**（按风格区分）

## 输出风格

| 维度 | formal | brief |
|------|--------|-------|
| 输出 | 完整资金分析报告 | 资金方向一句话 |
| 分层 | 4层（超大/大/中/小） | 仅主力（超大+大） |
| 趋势 | 近5/10/20日趋势 | 近3日方向 |
| 排名 | 全市场资金流Top20 | 仅标的数据 |

默认 brief。用户要求"详细"、"报告"、"完整分析"时用 formal。

## 关键规则

1. 主力资金流向是**辅助指标**，不能单独作为买卖依据
2. 资金流数据基于成交量拆分，存在一定估算误差
3. "主力资金流入"不等于"有人在买入"——买卖总是对等的，流向反映的是**大单主动性**
4. 涨停板缩量时主力净流入数据可能失真
5. 需结合股价走势解读：
   - 上涨 + 主力流入 = 趋势确认
   - 上涨 + 主力流出 = 出货嫌疑
   - 下跌 + 主力流入 = 逢低吸纳
   - 下跌 + 主力流出 = 趋势恶化
6. 所有金额统一用"万元"或"亿元"展示，保留2位小数
7. 参考 `references/money-flow-guide.md` 了解数据原理和信号矩阵

## 免责声明

在 formal 输出末尾附加：资金流向数据基于成交量估算，仅供参考，不构成投资建议。

## 使用示例

### 示例 1: 基本使用

```python
# 调用 skill
result = run_skill({
    "param1": "value1",
    "param2": "value2"
})
```

### 示例 2: 命令行使用

```bash
python scripts/run_skill.py --input data.json
```
