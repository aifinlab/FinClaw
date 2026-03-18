---
name: return-calculation
description: 用于区间/年化收益的收益率计算原子 skill，适用于通用行业金融计算场景。
---

# 收益率计算 Skill

## 数据来源

本 Skill 支持多种金融数据输入格式，核心数据来源包括：

### 1. 价格序列数据
- **股票价格数据**：开盘价、收盘价、最高价、最低价、成交量
- **基金净值数据**：单位净值、累计净值、分红信息
- **债券价格数据**：全价、净价、到期收益率
- **指数数据**：各类市场指数、行业指数、主题指数

### 2. 交易流水数据
- **交易记录**：买入价格、卖出价格、交易数量、交易日期
- **持仓数据**：持仓数量、持仓成本、当前市值
- **分红派息数据**：现金分红、股票分红、除权除息日期

### 3. 数据格式要求
- **CSV格式**：标准时间序列数据，包含日期和价格列
- **Excel格式**：支持多工作表价格数据
- **JSON格式**：结构化价格数据
- **数据库连接**：支持SQL数据库直接查询

> 说明：本 Skill 不包含数据采集功能，需要用户提供清洗后的价格数据。建议数据时间跨度不少于1年，以便进行年化收益率计算。

---

## 功能

本 Skill 提供全面的收益率计算能力，涵盖多种计算口径：

### 1. 区间收益率计算
- **简单收益率** = (期末价格 - 期初价格) / 期初价格 × 100%
- **对数收益率** = ln(期末价格 / 期初价格) × 100%
- **累计收益率** = (期末价格 - 期初价格) / 期初价格 × 100%
- **多期收益率** = (1 + r1) × (1 + r2) × ... × (1 + rn) - 1

### 2. 年化收益率计算
- **年化简单收益率** = (1 + 区间收益率)^(365/天数) - 1
- **年化对数收益率** = 区间对数收益率 × (365/天数)
- **考虑复利的年化收益率**：基于复利公式计算

### 3. 考虑分红的收益率计算
- **总收益率** = (期末价格 + 分红 - 期初价格) / 期初价格 × 100%
- **复权收益率**：考虑分红除权后的收益率
- **分红收益率** = 分红金额 / 期初价格 × 100%

### 4. 滚动收益率计算
- **滚动窗口收益率**：计算指定时间窗口内的滚动收益率
- **移动平均收益率**：基于移动平均价格计算收益率
- **分位数收益率**：计算收益率的分位数分布

### 5. 数据处理能力
- **缺失值处理**：支持前向填充、后向填充、插值等方法
- **异常值检测**：基于统计方法识别和处理异常价格
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
# 计算简单收益率
python scripts/calc_return.py --input prices.csv --date-col date --price-col close --output returns.csv

# 计算年化收益率
python scripts/calc_return.py --input prices.csv --date-col date --price-col close --output annual_returns.csv --annualize true

# 计算对数收益率
python scripts/calc_return.py --input prices.csv --date-col date --price-col close --output log_returns.csv --method log
```

### 3. 高级配置
```bash
# 考虑分红的收益率计算
python scripts/calc_return.py --input prices.csv --dividend-file dividends.csv --output total_returns.csv --include-dividend true

# 计算滚动收益率
python scripts/calc_return.py --input prices.csv --output rolling_returns.csv --window 30 --min-periods 20

# 指定时间区间
python scripts/calc_return.py --input prices.csv --output period_returns.csv --start-date 2024-01-01 --end-date 2024-12-31
```

### 4. 输出示例
```json
{
  "symbol": "000001.SZ",
  "period": "2024-01-01 to 2024-12-31",
  "returns": {
    "simple_return": 15.8,
    "log_return": 14.7,
    "annualized_return": 15.8,
    "total_return": 18.2,
    "dividend_yield": 2.4
  },
  "statistics": {
    "trading_days": 245,
    "max_return": 8.5,
    "min_return": -5.2,
    "volatility": 12.3
  },
  "rolling_returns": {
    "30_day": 2.1,
    "60_day": 4.5,
    "90_day": 7.8
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 价格数据需要经过清洗和验证
- 建议使用复权价格进行计算
- 异常价格数据会影响计算结果

### 2. 计算口径说明
- 不同计算方法的收益率结果可能不同
- 年化收益率需要明确交易日天数
- 分红处理方式会影响总收益率

### 3. 时间序列分析
- 收益率计算应结合时间序列分析
- 考虑市场波动对收益率的影响
- 不同时间区间的收益率不可直接比较

### 4. 综合判断原则
- 单一收益率指标不能全面反映投资表现
- 需要结合风险指标进行综合分析
- 应结合市场环境和行业特点进行判断

### 5. 使用限制
- 本 Skill 输出为技术分析结果，不构成投资建议
- 使用者应结合专业判断和具体业务场景
- 对于重大决策，建议咨询专业投资顾问

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 收益率计算公式手册
  - 年化收益率计算方法
  - 分红处理最佳实践指南
  - 数据处理方法说明文档

## License
- 本 skill 代码部分采用 MIT License，详见 `LICENSE` 文件
- 依赖与运行环境以 `requirements.txt` 为准
- 文档内容采用 CC BY 4.0 许可
