---
name: a-share-value-trap
description: A股价值陷阱/低估值陷阱识别。当用户说"价值陷阱"、"value trap"、"低估值陷阱"、"便宜有道理"、"为什么一直不涨"时触发。量化识别低估值股票是否为价值陷阱。支持formal和brief风格。
---
# A股价值陷阱/低估值陷阱识别
## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```
## Workflow
### Step 1: 获取财务+估值数据
### Step 2: 低估值筛选
PE/PB低于行业均值的股票
### Step 3: 价值陷阱信号检测
- 盈利持续下滑（净利润连续2+季度下降）
- 现金流恶化（经营现金流转负）
- 行业衰退（行业整体PE中枢下移）
- 治理风险（频繁并购/关联交易/变更审计师）
- 技术性破位（长期均线空头排列）
### Step 4: 价值vs陷阱评分
多维度打分判断是真便宜还是价值陷阱
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 低估原因 | 多维度分析 | 主要原因 |
| 陷阱信号 | 各信号检测结果 | 陷阱概率 |
| 建议 | 深度分析+建议 | 买/避 |
默认风格：brief。
## 关键规则
1. 低PE不等于便宜——盈利下滑会让PE先低后高
2. 低PB不等于安全——资产减值会让账面净资产缩水
3. 行业衰退是最大的价值陷阱来源
4. '便宜有便宜的道理'——需找到低估的真正原因
5. 价值投资需要催化剂——没有催化剂的低估可能持续很久
