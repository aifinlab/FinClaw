---
name: futures-delivery-analyzer
description: 期货交割分析工具。获取期货品种交割信息、交割仓库、交割成本、仓单数据。分析交割月流动性变化、逼仓风险。使用AkShare仓单数据、交易所交割规则。适用于交割月策略、期现回归交易。
---

# 期货交割分析器

## 功能

- 交割月份提醒与倒计时
- 交割规则查询（接入AkShare合约详情）
- 仓单数据实时查询（上期所、郑商所）
- 交割仓库信息
- 逼仓风险评估
- 多合约交割对比

## 数据源

- **AkShare交割数据**:
  - `futures_delivery_shfe(date)` - 上期所月度交割数据
  - `futures_delivery_czce(date)` - 郑商所月度交割查询  
  - `futures_delivery_dce(date)` - 大商所交割统计
- **AkShare仓单数据**:
  - `futures_shfe_warehouse_receipt()` - 上期所仓单日报
  - `futures_warehouse_receipt_czce()` - 郑商所仓单日报
- **合约详情**: `futures_contract_detail()` - 交易所交割规则

## 交割要素

| 要素 | 说明 |
|------|------|
| 交割月份 | 合约到期月份 |
| 最后交易日 | 合约最后交易日 |
| 最后交割日 | 交割截止日期 |
| 交割方式 | 实物交割/现金交割 |
| 仓单 | 标准仓单数量 |
| 升贴水 | 地区、品质差异调整 |

## 风险等级

| 等级 | 描述 | 建议 |
|------|------|------|
| normal | 正常 | 正常交易 |
| medium | 中等风险 | 密切关注 |
| high | 高风险 | 考虑移仓 |
| critical | 极高风险 | 立即平仓或移仓 |
| expired | 已过期 | 无法交易 |

## 使用方法

```bash
# 分析单个合约交割信息（包含仓单和交割数据）
python main.py --symbol RB2505

# 不包含仓单数据
python main.py --symbol RB2505 --no-warehouse

# 不包含交割统计数据
python main.py --symbol RB2505 --no-delivery

# 仅获取交割统计数据
python main.py --symbol RB --delivery-only

# 指定月份获取交割数据
python main.py --symbol RB --delivery-only --date 202503

# 对比多个合约交割时间
python main.py --compare RB2505,RB2510,HC2505
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| --symbol | 合约代码/品种代码 | RB2505, CU2506 |
| --no-warehouse | 不获取仓单数据 | - |
| --no-delivery | 不获取交割统计数据 | - |
| --delivery-only | 仅获取交割统计数据 | - |
| --date | 指定年月(YYYYMM) | 202503 |
| --compare | 对比多个合约 | RB2505,HC2505 |

## 输出字段

```json
{
  "delivery_info": {
    "delivery_year": 2025,
    "delivery_month": 5,
    "estimated_delivery_date": "2025-05-15",
    "days_to_delivery": 30,
    "last_trading_day": "合约月份15日",
    "last_delivery_day": "最后交易日后连续五个工作日",
    "delivery_method": "实物交割",
    "delivery_grade": "交割品级标准..."
  },
  "warehouse_receipt": {
    "total_quantity": 15000,
    "daily_change": -500,
    "warehouse_count": 8,
    "data_source": "futures_shfe_warehouse_receipt"
  },
  "delivery_stats": {
    "exchange": "SHFE",
    "date": "202503",
    "delivery_volume": 5000,
    "delivery_amount": 25000000,
    "data_source": "futures_delivery_shfe"
  },
  "risk_analysis": {
    "risk_level": "medium",
    "risk_level_desc": "中等风险",
    "warnings": ["临近交割月，流动性开始下降"],
    "suggestions": ["关注基差变化，考虑移仓"]
  }
}
```

## 更新日志

- 2025-03-25: 接入AkShare交割数据接口(futures_delivery_shfe/czce/dce)和仓单数据接口，提供交割统计和仓单双重数据源
