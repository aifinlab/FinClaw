# family-trust-designer

## 描述
家族信托智能设计工具，提供财富传承方案、资产隔离架构、税务优化策略、信托治理机制设计。

## 功能
- 家族信托架构设计（可撤销/不可撤销）
- 财富传承方案（代际传承、条件分配）
- 资产隔离策略
- 税务筹划建议
- 信托治理机制（保护人、受益人委员会）
- 分配条款设计
- 应急方案规划

## 使用场景
- 高净值客户家族传承规划
- 家族办公室服务
- 跨境财富配置
- 婚前/婚后财产隔离
- 企业股权传承

## 输入输出

### 输入
```json
{
  "client_profile": {
    "age": 55,
    "marital_status": "已婚",
    "children": [{"age": 25}, {"age": 20}],
    "total_assets": 500000000,
    "asset_types": ["股权", "房产", "现金", "保单"],
    "residency": "中国"
  },
  "objectives": ["财富传承", "资产隔离", "税务优化"],
  "constraints": {
    "minimum_income": 5000000,
    "distribution_conditions": ["结婚", "生育", "创业"]
  }
}
```

### 输出
```json
{
  "status": "success",
  "data": {
    "trust_structure": {
      "type": "不可撤销家族信托",
      "trustee": "信托公司",
      "protector": "委托人指定",
      "duration": "永续"
    },
    "asset_allocation": {
      "initial_funding": 200000000,
      "asset_types": ["现金", "保单", "股权"]
    },
    "distribution_scheme": {
      "generation_1": "生活保障",
      "generation_2": "教育+创业支持",
      "generation_3": "条件分配"
    },
    "governance": {
      "protector_powers": ["更换受托人", "调整分配"],
      "investment_committee": true
    }
  }
}
```

## 运行方式

```bash
python scripts/main.py --profile client.json --objectives "wealth_transfer,asset_protection"
```

## 依赖
- pydantic>=1.10.0

## 许可证
MIT License
