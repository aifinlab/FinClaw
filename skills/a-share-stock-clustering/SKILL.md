---
name: a-share-stock-clustering
description: A股股票聚类/相似股票发现。当用户说"聚类"、"clustering"、"相似股票"、"类似的股票"、"同类股票"、"走势相似"时触发。量化聚类分析股票相似性。支持formal和brief风格。
---

# A股股票聚类/相似股票发现

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取多股数据
### Step 2: 特征构建
- 收益率特征：日/周收益率序列
- 基本面特征：PE/PB/ROE/营收增速等
- 技术特征：波动率/Beta/动量等
### Step 3: 聚类分析
- K-Means聚类（需指定K）
- 层次聚类（树状图可视化）
- DBSCAN（自动发现簇数）
### Step 4: 簇特征分析
各簇的共同特征（行业/风格/基本面）
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 聚类结果 | 完整分簇列表 | 目标股所在簇 |
| 簇特征 | 各簇详细画像 | 同类股票 |
| 应用 | 配对交易候选 | Top 5相似股 |
默认风格：brief。

## 关键规则
1. 特征标准化是聚类的前提——不同量纲需归一化
2. K-Means对K值敏感——可用肘部法则或轮廓系数选K
3. 收益率相似不等于基本面相似——需分维度聚类
4. 聚类结果可用于配对交易候选筛选
5. 行业分类≠统计聚类——后者可能发现隐含关联

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
