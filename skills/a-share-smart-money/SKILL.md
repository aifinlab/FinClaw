---
name: a-share-smart-money
description: A股聪明钱指标/主力行为量化识别。当用户说"聪明钱"、"smart money"、"主力行为"、"大单分析"、"机构行为"、"量价背离"、"主力在干嘛"、"有没有主力进场"时触发。基于 cn-stock-data 获取资金流向和K线数据，量化识别机构/主力资金行为模式。支持研报风格（formal）和快速分析风格（brief）。
---

# A股聪明钱/主力行为识别 (a-share-smart-money)

## 数据源
通过 `cn-stock-data` 统一层获取：
- **fund_flow**: 个股资金流向（大单/中单/小单净流入）
- **kline**: 日K线（open/high/low/close/volume/amount）
- **quote**: 实时行情（辅助判断当前状态）

## 核心指标体系

### 1. 大单净流入占比 (Large Order Flow Ratio)
- 公式: `大单净流入 / 总成交额 × 100%`
- 阈值: >5% 强流入, 2%~5% 温和流入, -2%~2% 平衡, <-5% 强流出

### 2. OBV (On Balance Volume)
- 收盘上涨: OBV += 当日成交量; 下跌: OBV -= 当日成交量
- 关注 OBV 与价格的背离（价跌量增 = 吸筹信号）

### 3. A/D Line (Accumulation/Distribution)
- 公式: `CLV = ((close-low)-(high-close))/(high-low)`, `AD += CLV × volume`
- AD 持续上升但价格横盘 → 主力吸筹

### 4. MFI (Money Flow Index)
- 类似 RSI 但加入成交量权重，范围 0-100
- MFI > 80 超买（可能出货），MFI < 20 超卖（可能吸筹）

## 主力行为模式识别

| 模式 | 价格特征 | 量能特征 | 资金流特征 |
|------|---------|---------|-----------|
| 吸筹 accumulation | 低位横盘/缓跌 | 缩量后间歇放量 | 大单持续净流入 |
| 出货 distribution | 高位震荡/滞涨 | 高位放量 | 大单持续净流出 |
| 洗盘 washout | 急跌后快速收回 | 下跌缩量反弹放量 | 大单流出但占比小 |
| 拉升 markup | 连续上涨/突破 | 持续放量 | 大单强劲流入 |

## 工作流程
1. 调用 cn-stock-data 获取目标股票近 N 日资金流向 + K线数据
2. 保存为 JSON，调用 `scripts/smart_money_detector.py` 计算指标
3. 解读脚本输出的模式分类与置信度
4. 结合近期市场环境和个股基本面给出综合判断
5. 按用户偏好输出（formal / brief）

## 脚本调用
```bash
# 准备数据后调用
python scripts/smart_money_detector.py --flow flow.json --kline kline.json
# 可选: --days 20 (分析窗口，默认20)
```

## 输出格式

### formal（研报风格）
- 标题 + 股票信息
- 聪明钱指标总览表（大单占比/OBV趋势/AD方向/MFI值）
- 主力行为模式判定（模式名 + 置信度 + 证据链）
- 量价关系分析段落
- 近期关键信号时间线
- 风险提示与操作建议

### brief（快速分析风格）
- 一句话结论：主力在做什么（吸筹/出货/洗盘/拉升/无明显迹象）
- 关键指标速览（3-4个数字）
- 信号强度评级（强/中/弱）

## 注意事项
- 资金流向数据存在滞后性，不可作为唯一决策依据
- 大单定义因券商而异，跨数据源对比时需注意口径差异
- 短期资金流向噪声大，建议至少看 5-10 个交易日趋势
- 本分析为量化辅助工具，不构成投资建议

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
