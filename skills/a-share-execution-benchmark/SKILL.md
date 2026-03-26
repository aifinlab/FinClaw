---
name: a-share-execution-benchmark
description: A股执行基准/Implementation Shortfall分析。当用户说"执行基准"、"IS分析"、"implementation shortfall"、"执行质量"、"到达价"、"arrival price"、"执行评估"时触发。基于 cn-stock-data 获取数据，评估交易执行质量。支持 formal/brief 两种输出风格。
---

# 执行基准/IS分析助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **成交记录**: 实际成交价格与时间
- **行情数据**: 决策时/下单时/成交时价格
- **基准数据**: VWAP/TWAP/收盘价

## 分析工作流

### Step 1: 基准选择
- 到达价(Arrival Price)：下单时的市场价格
- VWAP：成交量加权平均价
- TWAP：时间加权平均价
- 收盘价(Close)：适合MOC订单评估

### Step 2: IS计算
- IS = (实际均价 - 基准价) / 基准价 × 方向
- 买入IS：实际均价>基准价为正(不利)
- 卖出IS：实际均价<基准价为正(不利)
- IS越小执行质量越好

### Step 3: IS归因分解
- 延迟成本：决策价→下单价的变动
- 市场冲击：下单价→成交均价的变动
- 时机成本：市场自然波动的影响
- 机会成本：未成交部分的潜在损失

### Step 4: 执行质量评估
- IS vs 预期IS：实际是否优于模型预测
- IS分布：统计所有交易的IS分布
- 按维度分析：标的/时段/订单大小/算法
- 改进建议：针对IS最大的维度优化

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# 执行质量评估报告

## 一、IS汇总
| 基准 | IS(bps) | 评级 |
|------|---------|------|

## 二、IS归因
[延迟/冲击/时机/机会成本]

## 三、维度分析
[按标的/时段/算法的IS]

## 四、改进建议
```

### brief 风格（快速分析）
```
## 执行质量速览
- Arrival Price IS = 5.2bps
- VWAP IS = -1.3bps (优于VWAP)
- 主要成本：市场冲击3.8bps
- 评级：良好(优于行业中位数)
```

参考 `references/execution-benchmark-guide.md` 获取详细方法论与 A股实证研究。

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
