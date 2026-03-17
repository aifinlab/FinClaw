---
name: a-share-correlation
description: A股相关性分析/联动关系/相关系数计算。当用户说"相关性"、"联动"、"correlation"、"XX和YY相关吗"、"哪些股票走势相似"、"分散化"、"对冲"、"beta"、"同涨同跌"、"相关性分析"、"相关系数"、"相关性矩阵"时触发。MUST USE when user asks about correlation analysis, correlation coefficient between stocks/sectors, or diversification analysis based on correlation. 计算个股/指数/行业之间的收益率相关系数、Beta值，分析联动关系和分散化效果，辅助组合构建和对冲决策。支持研报风格（formal）和快速查看风格（brief）。
---

# A股相关性分析 (Correlation & Co-movement Analysis)

## 数据源
通过 cn-stock-data skill 获取数据：
- `kline` 路由：多标的历史日K线（至少 1 年，推荐 2-3 年）
- `quote` 路由：实时行情、所属行业

计算工具：Python numpy/pandas
- `pandas.DataFrame.corr()` 计算皮尔逊相关系数矩阵
- `numpy` 做回归计算 Beta
- `pandas.DataFrame.rolling().corr()` 计算滚动相关性

## Workflow

### Step 1: 获取历史K线（多标的）
- 解析用户输入，识别 2-10 个标的（个股代码/指数代码/行业ETF）
- 通过 cn-stock-data 获取各标的日K线，时间跨度至少 1 年（默认 2 年）
- 同时获取大盘基准（沪深300 / 上证指数）作为 Beta 计算基准
- 对齐交易日，剔除停牌/缺失日期，确保数据完整性
- 计算日收益率序列：`r_t = (close_t - close_{t-1}) / close_{t-1}`

### Step 2: 计算相关系数矩阵（Correlation Matrix）
- 基于日收益率序列，计算皮尔逊相关系数矩阵
- 输出 N x N 矩阵表格，对角线为 1.0
- 标注相关性强度等级（参考 references/correlation-guide.md）：
  - |r| > 0.7：强相关（红色/深色标记）
  - 0.3 < |r| < 0.7：中等相关
  - |r| < 0.3：弱相关（绿色/浅色标记）
  - r < 0：负相关（特别标注）
- 找出最高/最低相关性配对，重点分析

### Step 3: Beta 计算
- 对每个标的，以大盘指数（默认沪深300）为基准计算 Beta：
  - `Beta = Cov(r_stock, r_market) / Var(r_market)`
- 解读 Beta 含义：
  - Beta > 1.2：高弹性，涨跌幅大于大盘
  - 0.8 < Beta < 1.2：与大盘同步
  - Beta < 0.8：防御型，波动小于大盘
  - Beta < 0：反向标的（极少见，如对冲类）
- 同时计算 R-squared（拟合优度），判断 Beta 的可靠性

### Step 4: 滚动相关性分析（Rolling Correlation）
- 计算 60 日滚动相关性（可自定义窗口期）
- 分析相关性的时间变化趋势：
  - 相关性是否稳定？波动区间？
  - 是否存在结构性变化（如某事件后相关性突增/骤降）？
  - 近期相关性 vs 长期相关性的偏离度
- 用文字描述滚动相关性走势（如"近3个月相关性从0.3升至0.7"）

### Step 5: 输出分析结果

**formal 风格**：
1. 分析概览：标的列表、数据区间、样本量
2. 相关系数矩阵（热力图描述 + 数据表格）
3. 关键配对分析（最强正相关、最强负相关、最弱相关各 top3）
4. Beta 分析表（含 R-squared）
5. 滚动相关性趋势分析
6. 分散化建议：基于相关性矩阵，推荐低相关组合
7. 风险提示

**brief 风格**（默认）：
1. 相关系数矩阵表格
2. 一句话总结：关键联动关系 + Beta 特征
3. 分散化结论：哪些标的适合同时持有
4. 风险提示

## 注意事项
- 相关性不稳定，会随市场环境变化，务必结合滚动相关性判断
- 极端行情（如股灾、熔断）下相关性趋向 1，分散化失效
- 相关不等于因果，不能仅凭高相关性推断业务联系
- 分散化需要真正低相关的资产，同行业/同概念股往往高度相关
- 停牌期间数据需剔除，否则会扭曲相关性计算
- 数据为历史统计结果，不构成投资建议
