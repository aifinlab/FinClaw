---
name: china-backtest-expert
description: 中国金融市场策略回测质量审查与验证专家。专为A股、期货、基金设计的研究纪律执行者，提供从假设定义到上线门禁的全流程质量把控。
version: 1.0.0
category: finance
tags: ["backtest", "quant", "A股", "策略验证", "质量门禁", "中国金融", "过拟合检测"]
complexity: advanced
author: FinSkillsHub
---

# China Backtest Expert

专为中国金融市场设计的专业级策略验证框架。不仅是回测执行工具，更是研究纪律的强制执行者和策略质量的守门员。

## 核心价值主张

1. **研究纪律强制化** - 将机构级量化研究规范固化为自动化检查点
2. **中国市场本土化** - 深度适配A股T+1、涨跌停、停牌、ST等特殊机制
3. **多源数据兼容** - 支持Tushare、AkShare、JoinQuant、本地文件等多种数据源
4. **结构化输出** - 不仅是文字报告，更是下游Skill可调用的质量判决

## 适用场景

- A股多因子策略回测前质量检查
- 期货CTA策略上线前验证
- 基金组合策略过拟合检测
- 研究所因子质量审查
- 量化私募策略门禁系统

## 核心检查维度

### 1. 假设定义与逻辑审查 (Hypothesis Validation)
检查项：
- 投资策略是否有清晰的经济逻辑
- 因子定义是否无歧义、可计算
- 信号生成逻辑是否与市场微观结构一致
- 持仓周期是否与T+1交易制度匹配

### 2. 数据质量与完整性 (Data Quality)
检查项：
- 数据时间范围是否覆盖完整市场周期
- 价格数据是否经过正确复权
- 是否处理停牌、退市、ST/*ST状态
- 指数成分股调整是否考虑幸存者偏差
- 财务数据发布时点是否准确（避免未来函数）

### 3. 交易制度合规性 (Market Regulation Compliance)
A股特殊检查：
- **T+1约束**: 当日买入股票是否在次日才可卖出
- **涨跌停限制**: 价格是否受±10%（ST±5%，创业板±20%）限制
- **停牌处理**: 停牌期间是否禁止交易
- **ST/*ST过滤**: 是否根据需求过滤风险警示股票
- **复权处理**: 分红送转后价格是否一致
- **流动性约束**: 是否设置最小成交额、换手率

成本模型：
- 买入: 佣金(万2.5) + 过户费(0.001%) + 经手费(0.00487%)
- 卖出: 佣金 + 印花税(0.1%) + 过户费 + 经手费
- 滑点: 基于成交量冲击的滑点估计

### 4. 统计严谨性 (Statistical Rigor)
检查项：
- **样本内/样本外划分**: 是否明确区分训练期、验证期、测试期
- **Walk-Forward Testing**: 是否进行滚动窗口验证
- **参数稳健性**: 参数微小变化是否导致结果剧烈变化
- **过拟合检测**: 使用CSCV(组合对称交叉验证)检测过拟合概率

### 5. 未来函数与数据泄露 (Look-ahead Bias)
严格检查：
- 是否使用未来信息计算当前信号
- 是否使用全样本统计量进行标准化
- 是否正确处理财报发布时点

### 6. 结果质量评估 (Result Quality)
评估维度：
- 夏普比率、最大回撤、胜率/盈亏比
- 信息比率（基准选择是否合理）
- 换手率（是否考虑T+1约束）
- 策略容量估计

### 7. 上线前质量门禁 (Go/No-Go Gate)

**PASS** (通过):
- 无未来函数，样本外夏普>1.0，过拟合概率<0.5

**REVISE** (需修改):
- 存在轻微数据质量问题，成本模型过于乐观

**REJECT** (拒绝):
- 存在严重未来函数，过拟合概率>0.7，考虑成本后收益为负

## 快速开始

### 安装
```bash
# 已进入OpenClaw环境
skillhub install finskillshub/china-backtest-expert
```

### CLI使用

```bash
# 检查本地回测结果
cd ~/.openclaw/workspace/skills/china-backtest-expert
python scripts/quality_gate.py \
  --strategy-file ./examples/pe_pb_strategy.py \
  --data-source tushare \
  --start-date 20180101 \
  --end-date 20231231 \
  --market ashare \
  --output-format json

# 完整质量门禁检查
python scripts/quality_gate.py \
  --backtest-result ./backtest_result.csv \
  --config ./examples/quality_config.yaml \
  --report ./quality_report.json
```

### Python API

```python
from scripts.quality_gate import QualityGate

# 初始化门禁
gate = QualityGate(
    market='ashare',
    data_source='tushare',
    cost_model='realistic',
    strict_level='institution'
)

# 运行检查
result = gate.review(
    strategy_code='./strategy.py',
    backtest_data='./backtest_df.csv',
    check_list='all'
)

# 获取判决
print(result['verdict'])  # PASS | REVISE | REJECT
print(result['overall_score'])  # 综合质量评分
```

## 配置示例

```yaml
# quality_config.yaml
market:
  type: ashare
  board: main
  st_filter: true
  min_cap: 1e8

trading:
  t1_constraint: true
  price_limit: true
  halt_handling: skip
  commission: 0.00025
  stamp_duty: 0.001
  slippage_model: volume_impact

data:
  adjust: post
  survivors_bias: correct

quality:
  oos_ratio: 0.3
  walk_forward: true
  cscv_trials: 16
  min_sharpe: 1.0
  max_drawdown: 0.25

output:
  format: structured
  language: zh
```

## 输入/输出规范

- **输入Schema**: `schemas/input_schema.json`
- **输出Schema**: `schemas/output_schema.json`

## 与其他Skill的协作

```python
# 与数据获取Skill协作
from akshare_stock import get_stock_data
from china_backtest_expert import QualityGate

# 获取数据
data = get_stock_data('600519', start='20200101', end='20231231')

# 质量检查
gate = QualityGate()
result = gate.review_data(data)

# 与策略执行Skill协作
if result['verdict'] == 'PASS':
    from quant_strategy import run_backtest
    backtest_result = run_backtest(strategy, data)
```

## 文档

- [A股回测最佳实践](./references/a_stock_best_practices.md)
- [成本模型详解](./references/cost_model_details.md)
- [过拟合检测方法](./references/overfitting_detection.md)

## 许可

MIT License © 2026 FinSkillsHub
