---
name: a-share-volatility
description: A股波动率分析/GARCH建模。当用户说"波动率"、"volatility"、"GARCH"、"波动率锥"、"历史波动率"、"隐含波动率"、"HV"、"IV"、"波动率分位"、"XX波动率多少"、"波动率高吗"时触发。分析个股/指数的历史波动率、波动率锥、GARCH预测、隐含波动率对比，辅助判断当前波动率水平和未来波动率趋势。支持研报风格（formal）和快速查看风格（brief）。
---

### 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
VOL_SCRIPTS="$SKILLS_ROOT/a-share-volatility/scripts"

# 日线 K 线（近 2 年，用于波动率锥和 GARCH 拟合）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [2年前日期]

# 实时行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]

# 波动率一键分析（HV多窗口 + 波动率锥 + GARCH预测 + EWMA）
python "$VOL_SCRIPTS/volatility_analyzer.py" --code [CODE] --start [2年前日期]

# 期权隐含波动率（仅限有期权的标的：50ETF/300ETF/个股期权）
# 通过 akshare 获取期权数据
python -c "import akshare as ak; df=ak.option_sse_greeks_sina(symbol='510050'); print(df[['IV']].describe())"
```

### Workflow (5 steps):

**Step 1: 数据获取与预处理**
1. 获取近 2 年日线 K 线数据（OHLCV）
2. 计算对数收益率：r_t = ln(Close_t / Close_{t-1})
3. 获取实时行情确认最新价格
4. 运行 `volatility_analyzer.py` 获取完整波动率分析结果

**Step 2: 历史波动率计算（多窗口）**
计算 5 个滚动窗口的年化历史波动率：

| 窗口 | 用途 | 说明 |
|------|------|------|
| HV5 | 超短期波动 | 反映近一周波动 |
| HV10 | 短期波动 | 反映近两周波动 |
| HV20 | 月度波动 | 最常用，对应期权月到期 |
| HV60 | 季度波动 | 中期波动水平 |
| HV120 | 半年波动 | 长期波动基准 |

计算方法（Close-to-Close）：
- HV_N = std(r_t, window=N) * sqrt(252) * 100（百分比形式）

补充方法（如果有高开低收数据）：
- **Parkinson 波动率**：利用最高价/最低价，HV_park = sqrt(1/(4N*ln2) * sum(ln(H/L)^2)) * sqrt(252)
- **Yang-Zhang 波动率**：综合开盘跳空 + 日内波动，更准确

**Step 3: 波动率锥构建**
对每个窗口，计算历史上所有滚动 HV 值的分位数分布：

| 分位数 | 含义 |
|--------|------|
| P95 | 极高波动（历史 95% 分位） |
| P75 | 偏高波动 |
| P50 | 中位数（典型水平） |
| P25 | 偏低波动 |
| P05 | 极低波动（历史 5% 分位） |

**当前 HV 在锥中的位置**：
- 高于 P75 → 波动率偏高，可能回归
- P25-P75 → 正常区间
- 低于 P25 → 波动率偏低，可能扩张

波动率锥呈现方式：以窗口为横轴、波动率为纵轴，各分位线形成"锥形"，当前值标注在对应位置。

**Step 4: GARCH(1,1) 拟合与预测**
使用 `arch` 库拟合 GARCH(1,1) 模型（不可用时 fallback 到 EWMA）：

**GARCH(1,1) 模型**：
- sigma_t^2 = omega + alpha * r_{t-1}^2 + beta * sigma_{t-1}^2
- 长期方差 = omega / (1 - alpha - beta)
- alpha：短期冲击敏感度（越大越受近期波动影响）
- beta：波动率持续性（越大波动聚集越强）
- alpha + beta → 1：波动率持续性极强

**GARCH 预测输出**：
- 未来 5/10/20 日波动率预测值
- 向长期均值收敛的速度
- 参数解读（alpha/beta/omega）

**EWMA 备选**（lambda=0.94, RiskMetrics 标准）：
- sigma_t^2 = lambda * sigma_{t-1}^2 + (1-lambda) * r_{t-1}^2

**Step 5: HV vs IV 对比（如有期权数据）**
仅限有期权的标的（50ETF/300ETF 等）：
- 如果 IV > HV：期权定价偏贵，适合卖方策略
- 如果 IV < HV：期权定价偏低，适合买方策略
- IV-HV 差值的历史分位数

### 风格说明
| 维度 | formal（波动率研究报告） | brief（快速波动率查看） |
|------|----------------------|----------------------|
| 篇幅 | 2-4 页 | 半页 |
| HV 多窗口 | 5 个窗口全部列出 + 趋势判断 | HV20 + HV60 两个关键窗口 |
| 波动率锥 | 完整分位数表 + 文字描述锥形 | 当前 HV20 所处分位 |
| GARCH | 完整参数 + 预测 + 模型诊断 | 一句话预测方向 |
| IV 对比 | 详细 HV-IV 分析 + 策略建议 | IV vs HV 一句话 |
| 波动率特征 | 聚集性/均值回归/非对称性分析 | 省略 |
| 结论 | 多维度总结 + 波动率交易建议 | 高/正常/低 + 趋势 |
| 免责声明 | 需要 | 不需要 |

### 关键规则
1. **年化处理**：所有波动率统一年化（*sqrt(252)），以百分比形式呈现
2. **波动率锥判断**：核心输出是"当前波动率在历史中的位置"，必须给出分位数
3. **均值回归**：波动率具有均值回归特性，极端值倾向回归到长期均值
4. **波动率聚集**：高波动之后往往跟随高波动，低波动之后往往跟随低波动
5. **GARCH 可选**：如果 arch 库未安装，使用 EWMA 替代，结果标注为"EWMA 估计"
6. **IV 数据有限**：仅部分 ETF 和个股有期权，无期权标的跳过 IV 对比环节
7. **A 股特色**：注意涨跌停板对波动率计算的影响（涨跌停日波动率被低估），T+1 交易制度，新股上市初期波动率异常
8. **数据量要求**：GARCH 拟合建议至少 250 个交易日数据，波动率锥建议 2 年以上数据
