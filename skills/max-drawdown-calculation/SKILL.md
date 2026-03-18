---
name: max-drawdown-calculation
description: 用于回撤指标的最大回撤计算原子 skill，适用于通用行业金融计算场景。
---

# 最大回撤计算 Skill

## 数据来源

本 Skill 支持多种金融数据输入格式，核心数据来源包括：

### 1. 价格序列数据
- **股票价格数据**：日收盘价、周收盘价、月收盘价
- **基金净值数据**：单位净值、累计净值
- **组合净值数据**：组合累计净值序列
- **指数数据**：各类市场指数、行业指数

### 2. 净值数据
- **累计净值序列**：已计算的累计净值数据
- **收益率序列**：基于收益率计算的累计净值
- **回撤序列**：历史回撤数据

### 3. 数据格式要求
- **CSV格式**：标准时间序列数据，包含日期和价格/净值列
- **Excel格式**：支持多工作表数据
- **JSON格式**：结构化时间序列数据
- **数据库连接**：支持SQL数据库直接查询

> 说明：本 Skill 不包含数据采集功能，需要用户提供清洗后的价格或净值数据。建议数据时间跨度不少于1年，以便进行准确的最大回撤计算。

---

## 功能

本 Skill 提供全面的最大回撤计算能力，涵盖多种计算方法：

### 1. 最大回撤计算
- **绝对最大回撤** = (峰值 - 谷值) / 峰值 × 100%
- **相对最大回撤**：相对于初始值的最大回撤
- **滚动最大回撤**：计算指定时间窗口内的滚动最大回撤
- **分段最大回撤**：计算不同时间段的最大回撤

### 2. 回撤指标计算
- **最大回撤持续时间**：从峰值到谷值的时间长度
- **回撤恢复时间**：从谷值恢复到峰值的时间长度
- **回撤频率**：统计回撤发生的频率
- **平均回撤**：计算平均回撤水平

### 3. 回撤分析
- **回撤分布**：分析回撤的分布特征
- **回撤趋势**：分析回撤的时间趋势
- **回撤预警**：设置回撤阈值进行预警

### 4. 回撤对比
- **与基准对比**：与基准指数的回撤对比
- **与同类对比**：与同类产品的回撤对比
- **历史对比**：与历史回撤水平对比

### 5. 数据处理能力
- **缺失值处理**：支持前向填充、插值等方法
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
# 计算最大回撤
python scripts/calc_max_drawdown.py --input prices.csv --date-col date --price-col close --output drawdown.csv

# 计算滚动最大回撤
python scripts/calc_max_drawdown.py --input prices.csv --date-col date --price-col close --output rolling_drawdown.csv --window 30

# 计算分段最大回撤
python scripts/calc_max_drawdown.py --input prices.csv --date-col date --price-col close --output period_drawdown.csv --period monthly
```

### 3. 高级配置
```bash
# 计算回撤持续时间
python scripts/calc_max_drawdown.py --input prices.csv --date-col date --price-col close --output drawdown_analysis.csv --include-duration true

# 与基准对比
python scripts/calc_max_drawdown.py --input prices.csv --benchmark benchmark.csv --output comparison.csv --compare-benchmark true

# 设置回撤预警阈值
python scripts/calc_max_drawdown.py --input prices.csv --date-col date --price-col close --output alert.csv --threshold 0.1
```

### 4. 输出示例
```json
{
  "symbol": "000001.SZ",
  "period": "2024-01-01 to 2024-12-31",
  "max_drawdown": {
    "absolute_drawdown": 25.8,
    "relative_drawdown": 25.8,
    "peak_date": "2024-06-15",
    "trough_date": "2024-08-20",
    "recovery_date": "2024-11-10",
    "duration_days": 66,
    "recovery_days": 82
  },
  "rolling_drawdown": {
    "30_day_max": 8.5,
    "60_day_max": 15.2,
    "90_day_max": 22.3
  },
  "statistics": {
    "average_drawdown": 5.2,
    "drawdown_frequency": 12,
    "max_drawdown_period": "2024-06 to 2024-08"
  },
  "distribution": {
    "percentile_25": 3.2,
    "percentile_50": 5.8,
    "percentile_75": 10.5
  }
}
```

---

## 注意事项与限制

### 1. 数据质量要求
- 价格或净值数据需要经过清洗和验证
- 建议使用足够长的历史数据（至少1年）
- 异常数据会影响最大回撤计算结果

### 2. 计算方法选择
- 不同计算方法的结果可能不同
- 滚动窗口大小会影响回撤计算结果
- 分段计算需要考虑时间段的合理性

### 3. 时间序列特性
- 最大回撤具有时间依赖性
- 不同时间区间的回撤不可直接比较
- 市场环境变化会影响回撤水平

### 4. 综合判断原则
- 单一回撤指标不能全面反映风险特征
- 需要结合其他风险指标进行综合分析
- 应结合市场环境和投资策略进行判断

### 5. 使用限制
- 本 Skill 输出为技术分析结果，不构成投资建议
- 使用者应结合专业判断和具体业务场景
- 对于重大决策，建议咨询专业投资顾问

---

## 参考资料
- 见 references/ 目录中的相关文档，包括：
  - 最大回撤计算公式手册
  - 回撤分析方法指南
  - 风险指标计算最佳实践
  - 数据处理方法说明文档

## License
- 本 skill 代码部分采用 MIT License，详见 `LICENSE` 文件
- 依赖与运行环境以 `requirements.txt` 为准
- 文档内容采用 CC BY 4.0 许可
