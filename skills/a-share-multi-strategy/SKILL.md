---
name: a-share-multi-strategy
description: A股多策略组合/策略配置分析。当用户说"多策略"、"multi strategy"、"策略组合"、"策略配置"、"怎么组合策略"、"策略相关性"时触发。基于 cn-stock-data 获取数据，量化分析多策略组合的协同效应。支持研报风格（formal）和快速分析风格（brief）。
---

# A股多策略组合/策略配置分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 策略池定义
列出候选策略（动量/价值/均值回归/事件驱动等），明确各策略逻辑。

### Step 2: 单策略回测
分别回测各策略的收益率序列、夏普比率、最大回撤。

### Step 3: 策略相关性分析
计算策略间收益率相关矩阵，识别低相关/负相关策略组合。

### Step 4: 策略权重优化
- 等权配置
- 风险平价（按波动率倒数加权）
- 最大夏普比率优化
- 最小相关性组合

### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 策略表现 | 各策略完整回测 | 夏普/回撤 |
| 相关矩阵 | 完整相关性热力图 | 平均相关系数 |
| 组合效果 | 多种配置方案对比 | 推荐配置 |

默认风格：brief。

## 关键规则
1. 低相关性策略组合才有分散化价值
2. 策略相关性在极端行情下会趋同（尾部相关性上升）
3. A 股策略容量有限——小盘策略尤其需要考虑冲击成本
4. 定期再平衡（月度/季度）优于漂移不管
5. 策略失效检测：滚动夏普比率跌破阈值时降权

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
