# trust-income-calculator

## 描述
信托收益计算与分配工具，支持预期收益测算、实际分配核算、IRR计算、税务筹划分析。

## 功能
- 预期收益计算（年化、累计、复利）
- 收益分配方案设计（按季/半年/年度/到期）
- 实际收益与预期对比
- IRR/XIRR计算
- 税务影响分析
- 费用扣除计算
- 收益再投资模拟

## 使用场景
- 产品发行前收益测算
- 投资者收益预估
- 收益分配执行
- 业绩归因分析
- 税务筹划

## 输入输出

### 输入
```json
{
  "calculation_type": "expected|actual|irr|tax",
  "principal": 1000000,
  "expected_yield": 7.5,
  "duration_months": 24,
  "distribution_way": "quarterly",
  "fee_structure": {
    "management_fee": 0.5,
    "custody_fee": 0.1,
    "performance_fee": 20
  },
  "tax_rate": 20
}
```

### 输出
```json
{
  "status": "success",
  "data": {
    "expected_return": {
      "gross_annual": 75000,
      "net_annual": 59100,
      "total_gross": 150000,
      "total_net": 118200,
      "net_yield": 5.91
    },
    "distribution_schedule": [
      {"date": "2026-06-20", "amount": 14775}
    ],
    "fee_breakdown": {
      "management": 10000,
      "custody": 2000,
      "performance": 0
    },
    "tax": {
      "taxable_amount": 118200,
      "tax_due": 23640,
      "after_tax_return": 94560
    }
  }
}
```

## 运行方式

```bash
# 预期收益计算
python scripts/main.py --principal 1000000 --yield 7.5 --duration 24

# IRR计算
python scripts/main.py --calc-type irr --cashflows data/cashflows.json

# 税务分析
python scripts/main.py --calc-type tax --principal 1000000 --return 118200
```

## 依赖
- numpy-financial>=1.0.0
- pandas>=1.5.0

## 许可证
MIT License
