# trust-compliance-checker

## 描述
信托合规智能审查工具，支持合格投资者识别、嵌套层级穿透、投资限制检查、关联交易识别等合规要点。

## 功能
- 合格投资者识别与适当性匹配
- 嵌套层级穿透检查
- 投资比例与集中度限制
- 关联交易识别
- 禁止性行为筛查
- 信息披露合规检查
- 生成合规意见书

## 使用场景
- 新产品设立合规审查
- 投资者适当性管理
- 关联交易监控
- 监管报送自查
- 合规培训案例生成

## 输入输出

### 输入
```json
{
  "check_type": "product|investor|transaction|nested",
  "product": {
    "product_code": "",
    "trust_type": "集合信托",
    "min_investment": 1000000,
    "investment_scope": ["非标债权", "股票", "债券"]
  },
  "investor": {
    "name": "",
    "investor_type": "自然人",
    "financial_assets": 5000000,
    "annual_income": 800000,
    "investment_experience": 5
  },
  "investments": [
    {"target": "XX资管计划", "amount": 5000000, "type": "嵌套投资"}
  ]
}
```

### 输出
```json
{
  "status": "success",
  "data": {
    "overall_compliance": "合规",
    "score": 92,
    "checks": {
      "investor_qualification": {
        "passed": true,
        "details": "金融资产500万，符合合格投资者标准"
      },
      "nested_structure": {
        "passed": true,
        "layers": 2,
        "穿透_result": "底层资产为标准化债券"
      },
      "concentration_limit": {
        "passed": false,
        "issues": ["单一非标债权占比18%，超过15%限制"]
      }
    },
    "recommendations": ["建议降低单一非标债权比例至15%以下"]
  }
}
```

## 运行方式

```bash
# 产品合规审查
python scripts/main.py --check-type product --product data/product.json

# 投资者适当性检查
python scripts/main.py --check-type investor --investor data/investor.json

# 关联交易识别
python scripts/main.py --check-type transaction --transactions data/transactions.json

# 嵌套层级穿透
python scripts/main.py --check-type nested --structure data/structure.json
```

## 依赖
- pydantic>=1.10.0
- networkx>=2.8.0
- jsonschema>=4.17.0

## 合规规则库

| 规则 | 说明 | 阈值 |
|---|---|---|
| 起投金额-集合 | 集合信托最低30万 | ≥300,000 |
| 起投金额-单一 | 单一信托最低100万 | ≥1,000,000 |
| 嵌套层数 | 禁止三层及以上嵌套 | ≤2层 |
| 非标集中度 | 单一非标≤15% | ≤15% |
| 房地产集中度 | 房地产信托≤30% | ≤30% |

## 免责声明
本工具基于公开监管规定，仅供参考。具体合规判断请咨询专业法律顾问。

## 许可证
MIT License
