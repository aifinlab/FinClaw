# trust-product-analyzer

## 描述
信托产品综合分析与筛选工具，支持产品信息抓取、风险评级、收益测算、合规检查和竞品对比。

## 功能
- 信托产品信息智能抓取与解析（支持用益信托网、中国信托登记等平台）
- 多维度风险评估（信用风险、市场风险、流动性风险）
- 预期收益与实际收益对比分析
- 合格投资者适当性匹配
- 产品竞品横向对比
- 自动生成尽调报告

## 使用场景
- 理财师为客户筛选合适信托产品
- 投资经理进行竞品分析
- 风控部门审查产品合规性
- 研究人员追踪市场产品发行情况

## 输入输出

### 输入
```json
{
  "action": "analyze|compare|screen",
  "product_code": "",
  "product_name": "",
  "filters": {
    "min_yield": 6.5,
    "max_duration": 24,
    "risk_level": ["R2", "R3"],
    "trust_type": "集合信托",
    "investment_type": "固定收益类"
  },
  "comparison_codes": [],
  "output_format": "json|markdown|pdf"
}
```

### 输出
```json
{
  "status": "success",
  "data": {
    "product": {
      "code": "XX信托-2026-001",
      "name": "XX号集合资金信托计划",
      "issuer": "XX信托有限公司",
      "type": "集合信托",
      "investment_type": "固定收益类",
      "risk_level": "R3",
      "min_investment": 1000000,
      "duration": 18,
      "expected_yield": 7.2,
      "distribution": "按季付息",
      "scale": 500000000
    },
    "risk_assessment": {
      "overall_score": 72,
      "level": "中等风险",
      "credit_risk": 65,
      "market_risk": 45,
      "liquidity_risk": 70
    },
    "underlying_analysis": {
      "assets": [],
      "concentration": 0.85,
      "credit_quality": "AA+"
    },
    "compliance_check": {
      "passed": true,
      "issues": []
    }
  },
  "metadata": {
    "source": "trust-product-analyzer",
    "version": "1.0.0",
    "timestamp": "2026-03-20T14:00:00Z"
  }
}
```

## 运行方式

```bash
# 分析单个产品
python scripts/main.py --action analyze --product-code "XX信托-2026-001"

# 产品对比
python scripts/main.py --action compare --codes "XX信托-2026-001,YY信托-2026-002"

# 条件筛选
python scripts/main.py --action screen --min-yield 7.0 --max-duration 24
```

## 依赖
- requests>=2.28.0
- beautifulsoup4>=4.11.0
- pandas>=1.5.0
- numpy>=1.23.0
- pydantic>=1.10.0
- akshare>=1.10.0  # 开源信托数据源

## 数据对接

本Skill已集成统一数据对接层，支持多数据源自动fallback：

| 优先级 | 数据源 | 类型 | 状态 |
|:---:|:---|:---|:---:|
| 1 | AkShare | 开源API | 无需注册 |
| 2 | 用益信托网 | 爬虫 | 公开数据 |
| 3 | 模拟数据 | Fallback | 保证可用 |

数据对接层自动选择可用数据源，无需手动配置。

## 数据来源
- AkShare开源金融数据
- 用益信托网（产品信息）
- 中国信托登记有限责任公司（行业统计）
- 信托公司产品说明书
- 公开募集说明书

## 免责声明
本工具提供的分析结果仅供参考，不构成投资建议。投资者应根据自身风险承受能力谨慎决策。

## 许可证
MIT License
