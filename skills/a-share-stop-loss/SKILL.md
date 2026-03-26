---
name: a-share-stop-loss
description: A股止损策略/风控规则量化。当用户说"止损"、"stop loss"、"止盈"、"风控"、"该不该割肉"、"设在哪"、"止损位"时触发。量化设计止损止盈策略。支持formal和brief风格。
---

# A股止损策略/风控规则量化

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取标的数据
### Step 2: 止损方法计算
- **固定比例止损**：从买入价下跌 N% 止损
- **ATR止损**：买入价 - N × ATR(14)
- **移动止损**：从最高价回撤 N% 止损
- **支撑位止损**：跌破关键技术支撑位
### Step 3: 历史回测
回测各止损方法在该股上的历史表现（避免的亏损 vs 误杀的盈利）
### Step 4: 最优止损参数
根据标的波动特征选择最优止损幅度
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 止损方案 | 多方法对比 | 建议止损位 |
| 回测结果 | 各方法胜率+收益 | 推荐方法 |
| 止盈建议 | 止盈策略 | 目标价位 |
默认风格：brief。

## 关键规则
1. 止损是风控底线——没有止损的交易不是投资
2. 止损幅度应匹配标的波动率——高波动股需更宽止损
3. A 股 T+1 下无法当日止损——需更谨慎的仓位管理
4. 止损位不应频繁修改——避免情绪化调整
5. 好的止损策略是在减少大亏和避免误杀之间的平衡

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
