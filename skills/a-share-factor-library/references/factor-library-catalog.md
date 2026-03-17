# A股量化因子库完整目录

> 共 7 大类 45+ 因子，每个因子包含：名称/英文/公式/cn-stock-data 字段映射/方向/适用行业

---

## 一、价值因子 (Value Factors) — 8 个

### 1. EP（盈利收益率 / Earnings-to-Price）
- **公式**: `EP = EPS_TTM / Price` 或 `EP = 1 / PE_TTM`
- **字段映射**: `quote → pe_ttm`（取倒数）；或 `finance → basic_eps` / `quote → price`
- **方向**: 正向（EP 越大 → 股票越便宜）
- **适用行业**: 全行业通用，但金融股（银行/保险）和周期股（钢铁/煤炭）的盈利波动大，需配合行业中性化

### 2. BP（账面市值比 / Book-to-Price）
- **公式**: `BP = 每股净资产 / Price`
- **字段映射**: `finance → net_asset_ps` / `quote → price`
- **方向**: 正向（BP 越大 → 账面资产折价越大）
- **适用行业**: 重资产行业效果好（银行/地产/制造），轻资产（科技/消费）参考价值有限

### 3. SP（营收市值比 / Sales-to-Price）
- **公式**: `SP = 每股营收 / Price`
- **字段映射**: `finance → total_rev`、需计算每股 = total_rev / 总股本；`quote → price, market_cap`
- **简化公式**: `SP = total_rev / market_cap`
- **方向**: 正向
- **适用行业**: 适合高营收低利润阶段的公司（互联网/创新药/早期成长股）

### 4. CFP（现金流市值比 / Cash-Flow-to-Price）
- **公式**: `CFP = 每股经营现金流 / Price`
- **字段映射**: `finance → oper_cf_ps` / `quote → price`
- **方向**: 正向（现金流充裕且股价便宜）
- **适用行业**: 全行业，尤其适合评估现金流质量（区分"纸面利润"和真实现金）

### 5. DP（股息率 / Dividend Yield）
- **公式**: `DP = 每股分红(近12月) / Price`
- **字段映射**: 需调用分红数据（adata dividend）或直接用 `quote` 中的股息率字段
- **方向**: 正向
- **适用行业**: 成熟稳定企业（银行/公用事业/高速公路），成长股通常不分红

### 6. EV/EBITDA（企业价值倍数）
- **公式**: `EV/EBITDA = (market_cap + 有息负债 - 现金) / EBITDA`
- **字段映射**: `quote → market_cap`；EBITDA 需从财报推算（净利润+利息+税+折旧摊销）
- **方向**: 负向（越低越便宜）
- **适用行业**: 跨国对比/并购估值常用，资本密集型行业（电信/能源/基建）效果好
- **注**: A 股直接字段有限，需多步推算

### 7. PEG（市盈率相对增长比率）
- **公式**: `PEG = PE_TTM / (净利润增速% × 100)`
- **字段映射**: `quote → pe_ttm`；`finance → net_profit_yoy_gr`
- **方向**: 负向（PEG < 1 通常认为被低估）
- **适用行业**: 成长股估值核心指标，不适用于利润为负或增速为负的公司

### 8. 股息率 TTM（Dividend Yield TTM）
- **公式**: `DY_TTM = 近12个月累计每股分红 / 当前股价`
- **字段映射**: 分红数据需单独获取
- **方向**: 正向
- **适用行业**: 同 DP

---

## 二、成长因子 (Growth Factors) — 6 个

### 1. 营收增速 (Revenue Growth YoY)
- **公式**: `rev_growth = (本期营收 - 去年同期营收) / 去年同期营收`
- **字段映射**: `finance → total_rev_yoy_gr`（直接提供同比增长率）
- **方向**: 正向
- **适用行业**: 全行业通用

### 2. 净利润增速 (Net Profit Growth YoY)
- **公式**: `profit_growth = (本期净利润 - 去年同期) / 去年同期`
- **字段映射**: `finance → net_profit_yoy_gr`
- **方向**: 正向
- **适用行业**: 全行业，注意剔除非经常性损益影响

### 3. ROE 变化 (ROE Change)
- **公式**: `roe_change = 本期ROE - 上期ROE`
- **字段映射**: `finance → roe_wtd`（需对比两期数据）
- **方向**: 正向（ROE 在改善）
- **适用行业**: 全行业，消费/科技股尤其看重

### 4. 毛利率变化 (Gross Margin Change)
- **公式**: `gm_change = 本期毛利率 - 上期毛利率`
- **字段映射**: `finance → gross_margin`（需对比两期）
- **方向**: 正向（毛利率提升意味着竞争力增强或涨价能力）
- **适用行业**: 制造业/消费品/科技

### 5. 研发增速 (R&D Growth)
- **公式**: `rd_growth = (本期研发费用 - 上期) / 上期`
- **字段映射**: 需财报详细数据，adata 43 字段中不直接提供，需从利润表获取
- **方向**: 正向（但需结合营收规模看研发强度）
- **适用行业**: 科技/医药/高端制造

### 6. 预期增速 (Expected Growth / Consensus)
- **公式**: `expected_growth = 分析师一致预期净利润增速`
- **字段映射**: 需券商一致预期数据源（如 Wind/Choice），cn-stock-data 暂不直接提供
- **方向**: 正向
- **适用行业**: 全行业
- **注**: 此因子需外部数据源补充

---

## 三、质量因子 (Quality Factors) — 8 个

### 1. ROE（净资产收益率 / Return on Equity）
- **公式**: `ROE = 归母净利润 / 平均股东权益`
- **字段映射**: `finance → roe_wtd`（加权 ROE）
- **方向**: 正向（ROE 越高盈利能力越强）
- **适用行业**: 全行业核心质量指标

### 2. ROA（总资产收益率 / Return on Assets）
- **公式**: `ROA = 净利润 / 平均总资产`
- **字段映射**: `finance → roa_wtd`
- **方向**: 正向
- **适用行业**: 跨行业对比时优于 ROE（消除杠杆差异）

### 3. ROIC（投入资本回报率 / Return on Invested Capital）
- **公式**: `ROIC = NOPAT / (总资产 - 流动负债) = 税后营业利润 / 投入资本`
- **字段映射**: 需从财报推算，`finance → net_profit_attr_sh` + 利息 + 税调整
- **方向**: 正向
- **适用行业**: 衡量真实经营效率，忽略资本结构差异

### 4. 毛利率 (Gross Margin)
- **公式**: `GM = (营收 - 营业成本) / 营收`
- **字段映射**: `finance → gross_margin`
- **方向**: 正向
- **适用行业**: 消费品/科技/制造，反映产品定价能力

### 5. 净利率 (Net Margin)
- **公式**: `NM = 净利润 / 营收`
- **字段映射**: `finance → net_margin`
- **方向**: 正向
- **适用行业**: 全行业，综合费用控制能力

### 6. 资产周转率 (Asset Turnover)
- **公式**: `AT = 营收 / 平均总资产`
- **字段映射**: `finance → total_asset_turn_days`（周转天数，取倒数转化）；或 `total_rev / total_assets` 手动计算
- **方向**: 正向（周转越快效率越高；周转天数越小越好）
- **适用行业**: 零售/制造/贸易

### 7. 应计比率 (Accruals Ratio)
- **公式**: `Accruals = (净利润 - 经营现金流) / 总资产`
- **字段映射**: `finance → net_profit_attr_sh, oper_cf_ps`（需 × 总股本还原），需总资产数据
- **方向**: 负向（应计比率越低，盈利质量越高）
- **适用行业**: 全行业，识别盈利操纵

### 8. 现金流/利润比 (Cash-to-Profit Ratio)
- **公式**: `CF_Ratio = 经营现金流 / 净利润`
- **字段映射**: `finance → oper_cf_ps / basic_eps`（近似）
- **方向**: 正向（>1 说明利润有真实现金支撑）
- **适用行业**: 全行业，尤其关注应收账款大的行业（建筑/环保）

---

## 四、动量因子 (Momentum Factors) — 6 个

### 1. 1月动量 (Momentum 1M)
- **公式**: `MOM_1M = (P_t / P_{t-20}) - 1`
- **字段映射**: `kline → close`（取最近 20 个交易日）
- **方向**: 正向（短期强势延续）
- **适用行业**: 全行业，短线交易常用

### 2. 3月动量 (Momentum 3M)
- **公式**: `MOM_3M = (P_t / P_{t-60}) - 1`
- **字段映射**: `kline → close`（取最近 60 个交易日）
- **方向**: 正向
- **适用行业**: 全行业

### 3. 6月动量 (Momentum 6M)
- **公式**: `MOM_6M = (P_t / P_{t-120}) - 1`
- **字段映射**: `kline → close`（取最近 120 个交易日）
- **方向**: 正向（中期趋势因子，学术研究最稳健）
- **适用行业**: 全行业

### 4. 12月动量 (Momentum 12M)
- **公式**: `MOM_12M = (P_t / P_{t-240}) - 1`
- **字段映射**: `kline → close`（取最近 240 个交易日）
- **方向**: 正向（长期动量，常跳过最近 1 个月避免反转效应）
- **适用行业**: 全行业
- **变体**: 12-1 月动量 = `(P_{t-20} / P_{t-240}) - 1`

### 5. 短期反转 (Short-Term Reversal 1W)
- **公式**: `REV_1W = (P_t / P_{t-5}) - 1`
- **字段映射**: `kline → close`（取最近 5 个交易日）
- **方向**: 负向（过去 1 周涨幅大的股票倾向回调）
- **适用行业**: 全行业，反转因子在 A 股效果显著

### 6. 52周新高距离 (Distance from 52W High)
- **公式**: `D52W = P_t / max(P_{past_240}) - 1`
- **字段映射**: `kline → close, high`（取过去 240 个交易日最高价）
- **方向**: 正向（接近新高的股票有突破动力；也可做反转用）
- **适用行业**: 全行业

---

## 五、波动率因子 (Volatility Factors) — 4 个

### 1. 历史波动率 (Historical Volatility)
- **公式**: `HV = std(日收益率) × sqrt(240)`（年化）
- **字段映射**: `kline → pct_change`（取过去 N 日，常用 20/60/240 日）
- **方向**: 负向（低波动率股票长期收益更高，即"低波动异象"）
- **适用行业**: 全行业

### 2. 特质波动率 (Idiosyncratic Volatility / IVOL)
- **公式**: `IVOL = std(Fama-French 三因子模型残差) × sqrt(240)`
- **字段映射**: 需回归残差计算，`kline → pct_change` + 市场/SMB/HML 因子
- **方向**: 负向（特质波动率低的股票预期收益高）
- **适用行业**: 全行业，学术量化常用
- **简化版**: 可用个股波动率减去市场 beta × 市场波动率近似

### 3. 下行波动率 (Downside Volatility)
- **公式**: `DV = std(min(日收益率, 0)) × sqrt(240)`
- **字段映射**: `kline → pct_change`（只取负收益日）
- **方向**: 负向
- **适用行业**: 全行业，风险厌恶型策略常用

### 4. Beta（系统性风险系数）
- **公式**: `Beta = cov(R_i, R_m) / var(R_m)`
- **字段映射**: `kline → pct_change`（个股）+ 沪深300指数收益率
- **方向**: 视策略而定（低 beta 稳健，高 beta 进攻）
- **适用行业**: 全行业
- **计算窗口**: 通常取过去 240 个交易日

---

## 六、规模因子 (Size Factors) — 3 个

### 1. 总市值 (Total Market Cap)
- **公式**: `MKT_CAP = 总股本 × 当前股价`
- **字段映射**: `quote → market_cap`
- **方向**: 负向（小市值股票有超额收益，即"小盘效应"）
- **适用行业**: 全行业

### 2. 流通市值 (Float Market Cap)
- **公式**: `FLOAT_CAP = 流通股本 × 当前股价`
- **字段映射**: `quote → float_market_cap`
- **方向**: 负向
- **适用行业**: 全行业，A 股更常用流通市值

### 3. 对数市值 (Log Market Cap)
- **公式**: `LN_CAP = ln(market_cap)`
- **字段映射**: `quote → market_cap`（取自然对数）
- **方向**: 负向
- **适用行业**: 全行业，取对数使分布更接近正态

---

## 七、流动性因子 (Liquidity Factors) — 4 个

### 1. 换手率 (Turnover Rate)
- **公式**: `TR = 成交量 / 流通股本`（日均，或 N 日均值）
- **字段映射**: `kline → turnover_rate`；或 `quote → turnover_rate`
- **方向**: 负向（低换手率股票长期超额收益更高）
- **适用行业**: 全行业

### 2. Amihud 非流动性指标 (Amihud Illiquidity)
- **公式**: `ILLIQ = mean(|日收益率| / 日成交额)`
- **字段映射**: `kline → pct_change, amount`（取过去 N 日均值）
- **方向**: 正向（非流动性越高 → 流动性越差 → 流动性溢价越大）
- **适用行业**: 全行业，小盘股/ST 股需注意极端值
- **计算窗口**: 通常取过去 20 或 60 日

### 3. 日均成交额 (Average Daily Amount)
- **公式**: `AVG_AMT = mean(日成交额, N日)`
- **字段映射**: `kline → amount`
- **方向**: 负向（低成交额=低流动性=潜在溢价，但需控制极端值）
- **适用行业**: 全行业

### 4. 买卖价差代理 (Bid-Ask Spread Proxy)
- **公式**: `SPREAD = 2 × (high - low) / (high + low)`
- **字段映射**: `kline → high, low`
- **方向**: 正向（价差大 → 流动性差 → 潜在溢价）
- **适用行业**: 全行业，日内数据更准确，日线数据为近似

---

## 八、技术因子 (Technical Factors) — 6 个

### 1. RSI（相对强弱指标 / Relative Strength Index）
- **公式**: `RSI = 100 - 100/(1 + avg_gain/avg_loss)`（N=14 日常用）
- **字段映射**: `kline → pct_change`（分离涨跌幅计算均值）
- **方向**: 中性（>70 超买信号，<30 超卖信号）
- **适用行业**: 全行业，趋势行情中可能失效

### 2. MACD 信号 (MACD Signal)
- **公式**: `DIF = EMA12(close) - EMA26(close)`; `DEA = EMA9(DIF)`; `MACD = 2×(DIF-DEA)`
- **字段映射**: `kline → close`
- **方向**: 正向（DIF 上穿 DEA 为金叉，看多）
- **适用行业**: 全行业

### 3. 均线偏离度 (MA Deviation)
- **公式**: `MA_DEV = (close - MA_N) / MA_N`（N=20/60/120/250）
- **字段映射**: `kline → close`（计算 N 日均线后求偏离）
- **方向**: 视策略（正偏离大→超买→均值回归；或→趋势延续）
- **适用行业**: 全行业

### 4. 量比 (Volume Ratio)
- **公式**: `VR = 当日成交量 / MA5(成交量)`
- **字段映射**: `quote → volume_ratio`；或 `kline → volume` 手动计算
- **方向**: 正向（量比>1 放量，配合价格突破使用）
- **适用行业**: 全行业

### 5. OBV 斜率 (On-Balance Volume Slope)
- **公式**: `OBV = cumsum(sign(pct_change) × volume)`；`OBV_slope = linreg_slope(OBV, N日)`
- **字段映射**: `kline → pct_change, volume`
- **方向**: 正向（OBV 上升斜率 → 量价配合良好）
- **适用行业**: 全行业

### 6. 波动率突破 (Volatility Breakout)
- **公式**: `VB = (close - open) / (high - low)`
- **字段映射**: `kline → open, close, high, low`
- **方向**: 正向（接近 1 说明收盘在日内高位，上涨动能强）
- **适用行业**: 全行业，日内趋势判断

---

## 因子方向速查表

| 方向 | 因子 |
|------|------|
| **正向（越大越好）** | EP, BP, SP, CFP, DP, ROE, ROA, ROIC, 毛利率, 净利率, 资产周转率, 现金流/利润, 营收增速, 净利润增速, ROE变化, 毛利率变化, 动量(1M/3M/6M/12M), Amihud, 买卖价差代理 |
| **负向（越小越好）** | EV/EBITDA, PEG, 应计比率, 短期反转, 历史波动率, 特质波动率, 下行波动率, 总市值, 流通市值, 对数市值, 换手率, 日均成交额 |
| **中性/视策略** | Beta, RSI, MACD, 均线偏离, 量比, OBV斜率, 波动率突破, 52周新高距离 |
