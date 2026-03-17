---
name: a-share-factor-timing
description: A股因子择时/风格轮动量化/大小盘价值成长风格切换。当用户说"因子择时"、"factor timing"、"风格轮动"、"什么风格在涨"、"大盘还是小盘"、"价值还是成长"、"风格切换"、"因子轮动"、"大盘小盘占优"、"价值成长占优"、"风格择时"时触发。MUST USE when user asks about factor timing, style rotation between value/growth or large/small cap, or which investment style is currently outperforming. 基于 cn-stock-data 获取数据，量化分析因子/风格的轮动节奏。支持研报风格（formal）和快速分析风格（brief）。
---

# A股因子择时/风格轮动量化

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 获取风格指数
获取大盘/小盘、价值/成长、高波/低波等风格指数K线。

### Step 2: 计算因子收益
- 各风格因子的多空收益（做多因子值高的、做空因子值低的）
- 滚动IC（因子预测力变化）

### Step 3: 因子动量分析
- 近期强势因子（过去20日因子收益排名）
- 因子动量：近5日因子收益 vs 近60日均值
- 因子拥挤度：因子估值扩散度

### Step 4: 择时信号
- 宏观信号：利率/信用利差/PMI → 因子偏好
- 技术信号：因子价差的均值回归
- 情绪信号：因子拥挤度过高时反转

### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| 因子表现 | 各因子收益+IC | 当前强势因子 |
| 轮动信号 | 多维度择时评分 | 推荐风格 |
| 历史规律 | 因子轮动周期分析 | 无 |

默认风格：brief。

## 关键规则
1. 因子择时难度极高——多数学术研究表明因子择时不如长期持有
2. 宏观驱动的风格轮动相对可预测（利率→价值/成长切换）
3. 因子拥挤度是最有效的反转信号之一
4. A 股风格轮动比海外更剧烈——大小盘轮动尤为明显
5. 保持因子分散化比精准择时更重要
