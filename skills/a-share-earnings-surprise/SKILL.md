---
name: a-share-earnings-surprise
description: A股业绩超预期/低预期量化分析。当用户说"业绩超预期"、"earnings surprise"、"超预期"、"低预期"、"业绩打败预期"、"不及预期"时触发。量化分析业绩公告后的市场反应。支持formal和brief风格。
---
# A股业绩超预期/低预期量化分析
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取财务数据和K线
### Step 2: 计算业绩超预期度
- SUE = (实际EPS - 预期EPS) / |预期EPS|
- 或用 实际净利润 vs 上期同比趋势线
### Step 3: 事件效应分析
- 业绩公告后T+1/T+3/T+5/T+20的CAR
- 区分超预期和低预期的不对称效应
### Step 4: 业绩漂移（PEAD）
分析业绩公告后的收益率漂移持续性
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 超预期度 | SUE计算+排名 | 超/达/低预期 |
| 市场反应 | CAR序列分析 | 公告后涨跌 |
| 漂移分析 | PEAD统计 | 漂移方向 |
默认风格：brief。
## 关键规则
1. A股业绩漂移效应（PEAD）显著存在——超预期后继续涨
2. 负面业绩反应通常比正面更剧烈（不对称效应）
3. 业绩预告vs正式报告可能有差异——两次都需关注
4. 分析师一致预期是衡量超预期的最佳基准（如有）
5. 业绩公告通常盘后发布——T+1为首个反应日

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
