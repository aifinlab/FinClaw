---
name: a-share-volume-price
description: A股量价关系量化分析。当用户说"量价"、"volume price"、"缩量"、"放量"、"量价背离"、"天量天价"、"地量地价"、"换手率分析"、"成交量异常"时触发。基于 cn-stock-data 获取K线数据，量化分析量价关系模式，识别异常量价信号。支持研报风格（formal）和快速分析风格（brief）。
---

# A股量价关系量化分析

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
```

**量化计算**：
```bash
QSCRIPTS="$SKILLS_ROOT/a-share-volume-price/scripts"
python "$QSCRIPTS/volume_price_analyzer.py" --data kline.json --window 20
```

## Workflow

### Step 1: 获取K线数据
获取包含 OHLCV（开高低收量）的K线数据。

### Step 2: 计算量价指标
- **VWAP**：成交量加权平均价
- **OBV**：能量潮，累计量（涨加跌减）
- **VR（量比）**：今日成交量 / 过去N日平均成交量
- **换手率 Z-score**：当前换手率相对历史的标准化值

### Step 3: 识别量价模式
8 种经典量价关系：量增价升/量增价跌/量缩价升/量缩价跌/量增价平/量缩价平/量平价升/量平价跌

### Step 4: 异常检测
- 成交量 > 均值 + 2σ → 放量异常
- 成交量 < 均值 - 1.5σ → 极度缩量
- 量价背离：价格新高但成交量未创新高

### Step 5: 输出

| 维度 | formal | brief |
|------|--------|-------|
| 指标 | 全部量价指标 | VR+OBV方向 |
| 模式 | 近期模式序列分析 | 当日模式 |
| 异常 | 历史异常回测 | 有/无异常 |

默认风格：brief。

## 关键规则
1. 量在价先——成交量变化往往领先于价格变化
2. A 股集合竞价量有特殊含义（开盘前15分钟）
3. 涨跌停板的成交量需特殊处理（封板量 vs 开板量）
4. 换手率比成交量更具可比性（剔除了流通盘大小差异）
5. 量价背离是趋势衰竭的重要信号

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
