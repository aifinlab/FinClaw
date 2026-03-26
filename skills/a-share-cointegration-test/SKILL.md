---
name: a-share-cointegration-test
description: A股协整检验/长期均衡关系分析。当用户说"协整"、"cointegration"、"长期均衡"、"价差平稳"、"XX和YY协整吗"时触发。量化检验股票间的协整关系。支持formal和brief风格。
---
# A股协整检验/长期均衡关系分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取多标的K线（价格序列）
### Step 2: 单位根检验
- ADF检验各序列是否I(1)
- KPSS检验辅助确认
### Step 3: 协整检验
- Engle-Granger两步法
- Johansen检验（多变量）
### Step 4: 误差修正模型
估计长期均衡关系和短期调整速度
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 单位根 | ADF+KPSS结果 | 是否I(1) |
| 协整 | 检验统计量+p值 | 是否协整 |
| 价差分析 | 半衰期+均值回归参数 | 配对可行性 |
默认风格：brief。
## 关键规则
1. 协整是配对交易的理论基础——两股价差均值回归
2. 协整关系可能随时间变弱或消失——需定期重新检验
3. 同行业股票协整概率更高但非必然
4. Johansen检验适合多变量，Engle-Granger适合两变量
5. 半衰期过长(>60日)的协整关系实战价值有限

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
