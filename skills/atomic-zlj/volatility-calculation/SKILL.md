---
name: volatility-calculation
description: 用于风险波动的波动率计算原子 skill，适用于通用行业金融计算场景。
---

# 波动率计算 Skill

## 数据来源

本 Skill 支持多种金融数据输入格式，核心数据来源包括：

### 1. 价格序列数据
- **股票价格数据**：日收盘价、周收盘价、月收盘价
- **基金净值数据**：单位净值、累计净值
- **债券价格数据**：全价、净价
- **指数数据**：各类市场指数、行业指数

### 2. 收益率数据
- **历史收益率序列**：已计算的收益率数据
- **对数收益率**：基于价格计算的对数收益率
- **简单收益率**：基于价格计算的简单收益率

### 3. 数据格式要求
- **CSV格式**：标准时间序列数据，包含日期和价格/收益率列
- **Excel格式**：支持多工作表数据
- **JSON格式**：结构化时间序列数据
- **数据库连接**：支持SQL数据库直接查询

> 说明：本 Skill 不包含数据采集功能，需要用户提供清洗后的价格或收益率数据。建议数据时间跨度不少于1年，以便进行准确的波动率计算。

---

## 功能

本 Skill 提供全面的波动率计算能力，涵盖多种计算方法：

### 1. 历史波动率计算
- **简单波动率** = 收益率序列的标准差 × √年化因子
- **对数波动率** = 对数收益率序列的标准差 × √年化因子
- **滚动波动率**：计算指定时间窗口内的滚动波动率
- **加权波动率**：基于时间加权的波动率计算

### 2. 年化波动率计算
- **日度年化** = 日收益率标准差 × √252
- **周度年化** = 周收益率标准差 × √52
- **月度年化** = 月收益率标准差 × √12
- **自定义年化**：根据交易日天数自定义年化因子

### 3. 条件波动率计算
- **GARCH模型波动率**：基于GARCH模型的条件异方差波动率
- **EWMA波动率**：指数加权移动平均波动率
- **已实现波动率**：基于高频数据的已实现波动率

### 4. 波动率指标
- **波动率分位数**：计算波动率的分位数分布
- **波动率趋势**：分析波动率的时间趋势
- **相对波动率**：相对于基准的波动率

### 5. 数据处理能力
- **缺失值处理**：支持前向填充、插值等方法
- **异常值检测**：基于统计方法识别和处理异常收益率
- **数据标准化**：支持不同数据源的格式统一
- **交易日调整**：自动识别交易日和非交易日

---

## 使用示例

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基础使用
```bash
# 计算历史波动率
python scripts/calc_volatility.py --input prices.csv --date-col date --price-col close --output volatility.csv

# 计算年化波动率
python scripts/calc_volatility.py --input prices.csv --date-col date --price-col close --output annual_volatility.csv --annualization 252

# 计算滚动波动率
python scripts/calc_volatility.py --input prices.csv --date-col date --price-col close --output rolling_volatility.csv --window 30
```

### 3. 高级配置
```bash
# 使用GARCH模型计算条件波动率
python scripts/calc_volatility.py --input returns.csv --output garch_volatility.csv --method garch

# 计算EWMA波动率
python scripts/calc_volatility.py --input returns.csv --output ewma_volatility.csv --method ewma --lambda 0.94

# 指定时间区间
python scripts/calc_volatility.py --input prices.csv --output period_volatility.csv --start-date 2024-01-01 --end-date 2024-12-31
```

### 4. 输出示例
```json
{
  "symbol": "000001.SZ",
  "period": "2024-01-01 to 2024-12-31",
  "volatility": {
    "historical_volatility": 18.5,
    "annualized_volatility": 18.5,
    "log_volatility": 18.2,
    "rolling_30d_volatility": 16.8,
    "rolling_60d_volatility": 17.5,
    "garch_volatility": 19.2
  },
  "statistics": {
    "trading_days": 245,
    "mean_return": 0.05,
    "max_volatility": 25.3,
    "min_volatility": 12.1
  },
  "distribution": {
    "percentile_25": 15.2,
    "percentile_50": 18.5,
    "percentile_75": 21.8
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 价格或收益率数据需要经过清洗和验证
- 建议使用足够长的历史数据（至少1年）
- 异常数据会影响波动率计算结果

### 2. 计算方法选择
- 不同计算方法的结果可能不同
- 年化因子需要根据实际交易日天数调整
- GARCH模型需要足够的样本量

### 3. 时间序列特性
- 波动率具有聚集性特征
- 不同时间区间的波动率不可直接比较
- 市场环境变化会影响波动率水平

### 4. 综合判断原则
- 单一波动率指标不能全面反映风险特征
- 需要结合其他风险指标进行综合分析
- 应结合市场环境和行业特点进行判断

### 5. 使用限制
- 本 Skill 输出为技术分析结果，不构成投资建议
- 使用者应结合专业判断和具体业务场景
- 对于重大决策，建议咨询专业投资顾问

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 波动率计算公式手册
  - GARCH模型使用指南
  - 年化波动率计算方法
  - 数据处理方法说明文档

## License
- 本 skill 代码部分采用 MIT License，详见 `LICENSE` 文件
- 依赖与运行环境以 `requirements.txt` 为准
- 文档内容采用 CC BY 4.0 许可
