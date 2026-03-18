---
name: akshare-margin-risk
description: 用于基于AkShare数据的保证金风险监控场景。适用于金融工作中的基础任务单元。
---

# AkShare A股保证金与风险敞口计算 Skill

## 数据来源

本 Skill 基于 **AkShare** 提供的 A 股市场公开数据接口构建，核心依赖如下：

1. `stock_margin_detail_sse(date=...)`
   - 来源：上海证券交易所融资融券明细
   - 用途：获取上交所标的证券在指定交易日的融资余额、融资买入额、融券余量、融券卖出量等数据
2. `stock_margin_detail_szse(date=...)`
   - 来源：深圳证券交易所融资融券交易明细
   - 用途：获取深交所标的证券在指定交易日的融资余额、融资买入额、融券余量、融券余额等数据
3. `stock_margin_sse(start_date=..., end_date=...)`
   - 来源：上海证券交易所融资融券汇总
   - 用途：获取交易所层面的融资融券总量与余额，用于市场环境校验与汇总监控
4. `stock_margin_szse(date=...)`
   - 来源：深圳证券交易所融资融券汇总
   - 用途：获取深交所单日两融汇总数据，用于市场环境校验与汇总监控
5. `stock_margin_underlying_info_szse(date=...)`
   - 来源：深圳证券交易所融资融券标的证券信息
   - 用途：校验证券是否为两融标的，以及是否允许当日融资/融券
6. `stock_zh_a_hist(symbol=..., period="daily", start_date=..., end_date=..., adjust="")`
   - 来源：东方财富 A 股历史行情
   - 用途：获取个股收盘价，用于头寸估值、风险敞口与情景损益计算

> 说明：本 Skill 使用 AkShare 对交易所与公开行情数据的封装，不直接连接券商交易系统，不包含账户真实授信额度、个体客户折算率、担保品折扣系数、维持担保比例等专有数据。默认输出适合作为 **研究、风控测算、盘前盘后估算**，不应替代券商柜台结果。

---

## 功能

本 Skill 面向 A 股两融场景，提供以下能力：

### 1. 保证金测算
- 按证券维度估算多头融资与空头融券的保证金占用
- 支持自定义：
  - 融资保证金比例（默认 100%）
  - 融券保证金比例（默认 100%）
  - 维持担保比例（默认 130%）
- 支持把现金、多头市值、空头市值、融资负债、融券负债拆分展示

### 2. 风险敞口计算
- 计算组合层面的：
  - 总市值
  - 多头敞口
  - 空头敞口
  - 净敞口
  - 总敞口
  - 杠杆倍数
- 支持按个股输出风险贡献与敞口排序

### 3. 两融明细对齐
- 根据指定交易日自动抓取上交所 / 深交所两融明细
- 自动标准化字段，统一为同一张风险底表
- 可将组合持仓与市场两融数据合并，识别组合是否属于两融标的，及其市场两融余额特征

### 4. 压力测试
- 支持单因子价格冲击，例如：
  - 全组合下跌 5%
  - 创业板下跌 8%
  - 指定股票上涨 / 下跌若干比例
- 输出冲击后的：
  - 权益变化
  - 保证金缺口
  - 维持担保比例变化
  - 预警状态

### 5. 命令行执行
- 通过 JSON 持仓文件直接运行
- 输出 JSON 结果，便于二次集成到调度脚本、风控平台或 notebook

---

## 使用示例

### 目录结构

```text
akshare_margin_risk_skill/
├── skill.md
└── scripts/
    └── calculate_margin_risk.py
```

### 安装依赖

```bash
pip install akshare pandas numpy
```

### 持仓文件示例

保存为 `portfolio.json`：

```json
{
  "trade_date": "2025-04-11",
  "cash": 3000000,
  "positions": [
    {
      "symbol": "600000",
      "name": "浦发银行",
      "side": "long",
      "shares": 300000,
      "financed_shares": 150000
    },
    {
      "symbol": "000001",
      "name": "平安银行",
      "side": "long",
      "shares": 200000,
      "financed_shares": 50000
    },
    {
      "symbol": "300750",
      "name": "宁德时代",
      "side": "short",
      "shares": 10000
    }
  ],
  "assumptions": {
    "long_margin_ratio": 1.0,
    "short_margin_ratio": 1.0,
    "maintenance_margin_ratio": 1.3,
    "default_price_shock": -0.05
  }
}
```

### 运行方式

```bash
python scripts/calculate_margin_risk.py --portfolio portfolio.json
```

### 输出内容

脚本会输出：
- 组合摘要
- 分证券敞口明细
- 两融市场辅助信息
- 压力测试结果

也可指定输出文件：

```bash
python scripts/calculate_margin_risk.py --portfolio portfolio.json --output result.json
```

---

## 交易说明

1. **融资头寸**
   - 对多头持仓，`financed_shares` 表示通过融资买入形成的数量
   - 融资负债默认按 `financed_shares × 收盘价` 估算
   - 若市场明细可用，则会附加展示对应证券在交易所口径下的融资余额与融资买入额

2. **融券头寸**
   - 对空头持仓，`shares` 视为融券卖出数量
   - 融券负债默认按 `shares × 收盘价` 估算
   - 若市场明细中存在 `融券余额`，将作为市场参考字段输出

3. **保证金口径**
   - 本 Skill 的默认口径是研究型估算口径，不等同于券商实时风控口径
   - 真实业务中，券商通常还会考虑：
     - 担保品折算率
     - 个股风险分级
     - 集中度限制
     - 停牌与涨跌停限制
     - 科创板 / 创业板 / ETF 等差异化规则
     - 实时价格而非收盘价

4. **维持担保比例**
   - 这里采用简化定义：
     - `维持担保比例 = 账户权益 / (融资负债 + 融券负债)`
   - 若融资负债与融券负债之和为 0，则视为无杠杆组合
   - 券商实务口径可能存在差异，请以实际业务规则为准

5. **适用场景**
   - 日终风控复盘
   - 盘前风险试算
   - 策略研究
   - 两融组合暴露度分析
   - 压力测试与预警

6. **不适用场景**
   - 实盘下单前的最终授信判断
   - 券商监管报送
   - 需要毫秒级实时行情或柜台字段的风控审批

---

## License

本 Skill 示例代码采用 **MIT License** 方式提供。你可以自由使用、修改和分发，但需自行评估其在生产环境中的适用性与合规性。

```text
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
```
