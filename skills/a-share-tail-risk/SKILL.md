---
name: a-share-tail-risk
description: A股尾部风险/黑天鹅/极端风险分析。当用户说"尾部风险"、"tail risk"、"黑天鹅"、"极端风险"、"肥尾"、"千股跌停"时触发。量化分析极端市场风险。支持formal和brief风格。
---

# A股尾部风险/黑天鹅/极端风险分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取长期K线数据
### Step 2: 尾部分布分析
- 计算收益率分布的偏度和峰度
- 拟合极值分布（GPD/GEV）
- 与正态分布对比尾部厚度
### Step 3: 极端事件统计
- 历史上超过3σ事件的频率和幅度
- 跌幅 > 5%的交易日统计
- 连续下跌天数分布
### Step 4: 尾部相关性
- 极端行情下个股/板块相关性变化
- 系统性风险传染路径
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 分布特征 | 偏度/峰度/QQ图 | 肥尾程度 |
| 极端事件 | 历史事件详细 | 近期风险 |
| 保护建议 | 对冲方案 | 风险等级 |
默认风格：brief。

## 关键规则
1. A股尾部风险显著高于成熟市场——涨跌停+T+1放大尾部效应
2. 正态分布严重低估尾部风险——需用t分布或极值分布
3. 危机时相关性趋向1——分散化在最需要时失效
4. 尾部对冲成本高——需权衡保护成本与风险暴露
5. 流动性风险在极端行情下放大——小盘股尤为严重

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
