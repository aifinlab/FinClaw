---
name: akshare-trend-judgment
description: 用于基于AkShare数据的趋势判断场景。适用于金融工作中的基础任务单元。
---

# AkShare A股趋势判断 Skill

## 数据来源

本 Skill 使用 **AkShare** 提供的 A 股公开市场数据接口，核心包括：

1. `stock_zh_a_hist`：获取沪深京 A 股历史日频行情，用于计算均线、收益率、波动率、回撤与突破信号。
2. `stock_zh_a_spot_em`：获取 A 股实时/最新股票列表与名称，用于证券代码校验和名称补全。

AkShare 官方文档说明，`stock_zh_a_hist` 可按股票代码、周期、日期区间与复权方式获取沪深京 A 股历史日频数据；`stock_zh_a_spot_em` 可获取 A 股市场行情快照与股票代码信息。数据源来自公开可访问的网站与行情页面，经 AkShare 封装后供 Python 调用。  
参考：AkShare 股票数据文档与数据说明。

## 功能

本 Skill 面向 **单只 A 股证券** 做规则化趋势判断，输出结构化结果，适合研究、投研辅助、风控预警和策略原型验证。

### 主要能力

- 拉取指定股票的历史日线行情
- 计算 MA5、MA10、MA20、MA60
- 计算 5/20/60 日收益率
- 计算 20 日年化波动率
- 计算近 60 日最大回撤
- 判断是否突破近 20 日高点或跌破近 20 日低点
- 综合规则输出趋势标签：
  - 强势上升趋势
  - 震荡偏强
  - 区间震荡
  - 震荡偏弱
  - 强势下降趋势
- 输出信号说明、趋势摘要与置信度

### 输出字段示例

- `symbol`: 股票代码
- `name`: 股票名称
- `as_of`: 截止日期
- `trend_label`: 趋势标签
- `confidence`: 置信度
- `close`, `ma5`, `ma10`, `ma20`, `ma60`
- `ret_5d`, `ret_20d`, `ret_60d`
- `annualized_volatility`
- `max_drawdown_60d`
- `signals`
- `summary`

## 使用示例

### 1. 安装依赖

```bash
pip install akshare pandas numpy
```

### 2. 运行脚本

```bash
python script/a_share_trend_judgment.py --symbol 600519 --start-date 20240101 --end-date 20260301
```

### 3. 输出到 JSON 文件

```bash
python script/a_share_trend_judgment.py \
  --symbol 000001 \
  --start-date 20240101 \
  --end-date 20260301 \
  --output result.json
```

### 4. 返回结果示意

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "as_of": "2026-03-01",
  "trend_label": "震荡偏强",
  "confidence": 0.69,
  "close": 1688.0,
  "ma5": 1679.2,
  "ma10": 1662.8,
  "ma20": 1645.6,
  "ma60": 1602.3,
  "ret_5d": 0.0132,
  "ret_20d": 0.0528,
  "ret_60d": 0.1085,
  "annualized_volatility": 0.2214,
  "max_drawdown_60d": -0.0821,
  "breakout_20d_high": false,
  "breakdown_20d_low": false,
  "signals": [
    "收盘价位于 MA20 之上且 MA20 高于 MA60",
    "短中期均线呈多头排列"
  ],
  "summary": "贵州茅台 截至 2026-03-01 的趋势判断为“震荡偏强”。收盘价 1688.00，MA20 1645.60，MA60 1602.30，20日涨跌幅 5.28%，20日年化波动率 22.14%。"
}
```

## 交易说明

1. 本 Skill 基于 **公开行情数据 + 规则判断**，适合做趋势研究与辅助决策，不构成任何投资建议。
2. 趋势判断结果依赖历史数据，无法保证对未来价格行为的预测准确性。
3. A 股存在涨跌停、停牌、除权除息、极端波动、行业轮动与政策冲击等情形，可能导致趋势信号失真。
4. 不同复权方式（不复权、前复权、后复权）会影响均线和收益率计算结果；默认使用前复权 `qfq`。
5. 建议将本 Skill 与基本面、成交量、公告、行业景气度和风险控制模块联合使用。
6. 若用于程序化交易前置筛选，应增加：
   - 流动性过滤
   - 停牌/ST 过滤
   - 风险事件过滤
   - 交易成本与滑点建模

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
