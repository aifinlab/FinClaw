---
name: a-share-execution-algo
description: A股算法执行/智能拆单策略。当用户说"算法执行"、"智能拆单"、"execution algo"、"算法交易"、"拆单策略"、"大单拆分"时触发。基于 cn-stock-data 获取数据，设计算法执行方案。支持 formal/brief 两种输出风格。
---

# 算法执行/智能拆单助手

## 数据获取

通过 cn-stock-data skill 获取数据：
- **分钟K线**: 日内成交量分布
- **实时行情**: 盘口深度与价格
- **历史成交**: 日均成交量/波动率

## 分析工作流

### Step 1: 算法选择
- TWAP：时间均匀拆分，适合流动性好的标的
- VWAP：按成交量分布拆分，机构最常用基准
- IS(Implementation Shortfall)：最小化执行缺口
- POV(Percentage of Volume)：按参与率执行

### Step 2: 参数配置
- 执行窗口：开始时间→结束时间
- 参与率上限：通常5-20%，避免过大市场冲击
- 价格保护：设置限价，超出范围暂停执行
- 紧急度：aggressive/neutral/passive

### Step 3: 实时调整
- 价格偏离监控：实际均价vs基准的偏差
- 成交量偏离：实际成交量vs预测的偏差
- 市场状态变化：波动率突增时降低执行速度
- 剩余量管理：尾盘加速完成剩余订单

### Step 4: 执行评估
- 执行均价 vs VWAP/TWAP/到达价
- 市场冲击成本估算
- 时机选择成本：延迟执行的机会成本
- 总执行成本 = 冲击 + 时机 + 佣金

### Step 5: 输出报告

## 输出格式

### formal 风格（研报级）
```
# [标的] 算法执行方案

## 一、方案配置
| 参数 | 设置 |
|------|------|
| 算法 | VWAP |
| 总量 | 50万股 |

## 二、执行计划
[分时段拆单明细]

## 三、风控参数
[价格保护、参与率]

## 四、预期成本
```

### brief 风格（快速分析）
```
## [标的] 执行方案速览
- VWAP算法，50万股，执行窗口9:30-14:30
- 参与率上限15%，预期冲击0.08%
- 价格保护：±1%
- 预期总成本：0.15%
```

参考 `references/execution-algo-guide.md` 获取详细方法论与 A股实证研究。

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
