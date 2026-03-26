---
name: a-share-financial-forensic
description: A股财务异常/财务造假预警量化。当用户说"财务异常"、"financial forensic"、"造假"、"财务造假"、"Beneish"、"M-score"、"财务粉饰"时触发。量化检测财务报表异常信号。支持formal和brief风格。
---
# A股财务异常/财务造假预警量化
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取多期财务数据
### Step 2: Beneish M-Score
计算8个变量的加权得分（>-1.78为操纵嫌疑）
### Step 3: 其他异常指标
- 应收账款增速 >> 营收增速
- 存货增速 >> 营收增速
- 经营现金流 vs 净利润严重背离
- 非经常性损益占比异常
- 关联交易占比高
### Step 4: 综合评分
多维度财务异常打分
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| M-Score | 各变量明细 | 综合得分 |
| 异常指标 | 全面检测结果 | 红旗数量 |
| 风险等级 | 历史对比分析 | 高/中/低 |
默认风格：brief。
## 关键规则
1. Beneish M-Score > -1.78 = 财务操纵嫌疑
2. 应收与营收增速严重背离是最常见的造假信号
3. 审计师意见非标(保留/无法表示)=重大红旗
4. A股造假特征：虚增营收+虚构现金流+体外循环
5. 财务异常≠必然造假——需结合行业特征判断

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
