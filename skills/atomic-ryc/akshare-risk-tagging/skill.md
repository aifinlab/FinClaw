---
name: akshare-risk-tagging
description: 用于基于AkShare数据的风险标签生成场景。适用于金融工作中的基础任务单元。
---

# AkShare A股风险标签打标 Skill

## 数据来源
本 Skill 使用 [AkShare](https://akshare.akfamily.xyz/) 提供的 A 股市场数据接口进行风险标签打标，主要包括：

1. `stock_zh_a_spot_em`：A 股实时行情快照，用于获取最新价、涨跌幅、成交量、成交额、换手率、市盈率等基础指标。
2. `stock_zh_a_hist`：A 股历史行情，用于计算近 N 日波动率、回撤、均线偏离、成交额均值等风险特征。
3. `stock_individual_info_em`：个股基础信息（如股票简称、总市值等），用于补充个股静态属性。

说明：不同 AkShare 版本的字段命名可能略有差异，脚本中已尽量兼容常见字段名，但建议在生产使用前结合实际环境验证一次。

## 功能
本 Skill 面向 A 股股票池进行**风险标签打标**，输出每只股票的风险标签、风险分数和综合风险等级。

### 已实现的风险标签
- `st_risk`：证券简称包含 `ST`、`*ST` 等特殊处理标识。
- `high_volatility_20d`：近 20 个交易日年化波动率偏高。
- `large_drawdown_60d`：近 60 个交易日最大回撤较大。
- `low_liquidity`：近 20 个交易日平均成交额偏低，流动性不足。
- `abnormal_turnover`：最新换手率异常偏高。
- `near_limit_down`：最新单日跌幅接近跌停风险区间。
- `penny_stock`：股价过低，价格脆弱性更高。
- `below_ma20`：股价低于 20 日均线，短期趋势偏弱。

### 综合输出
脚本会为每只股票输出：
- 股票代码
- 股票名称
- 最新价格
- 命中标签列表
- 风险分数
- 综合风险等级（`low` / `medium` / `high`）

### 输出文件
默认输出到：
- `output/risk_labels.csv`
- `output/risk_labels.json`

## 使用示例
### 1）安装依赖
```bash
pip install akshare pandas numpy
```

### 2）对默认股票池进行打标
```bash
python script/risk_labeling.py
```

### 3）指定股票代码列表
```bash
python script/risk_labeling.py --symbols 600519,000001,300750
```

### 4）限制处理股票数量（适合快速测试）
```bash
python script/risk_labeling.py --limit 50
```

### 5）指定输出目录
```bash
python script/risk_labeling.py --output-dir ./output
```

## 交易说明
1. 本 Skill 仅用于**研究、风控、预警、投前筛查**，不构成任何投资建议。
2. A 股存在涨跌停制度、ST 风险警示、停牌、低流动性、财务风险与事件驱动风险，模型标签只能反映部分可量化风险。
3. 风险标签是基于行情与基础信息规则生成，不等同于券商风控口径、交易所监管口径或基金/资管机构内部评级口径。
4. 建议将本 Skill 作为风控流水线的一部分，与基本面、公告、行业景气度、仓位管理和合规约束共同使用。
5. AkShare 数据源可能受网络、接口字段变更、上游网站结构变化影响，使用前应进行字段校验与异常处理。

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
