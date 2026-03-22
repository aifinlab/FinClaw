# 信托数据对接层使用指南

## 快速开始

### 1. 初始化数据对接层

```bash
cd finclaw/skills/trust-suite/data
python init_data.py
```

### 2. 在Skill中使用数据对接层

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))

from trust_data_adapter import get_data_provider

# 获取数据提供器
provider = get_data_provider()

# 获取产品数据
products = provider.get_products(min_yield=7.0, max_duration=24)

# 获取市场统计
stats = provider.get_market_stats()

# 获取收益率曲线
curve = provider.get_yield_curve()
```

## 数据源优先级

数据对接层按以下优先级尝试获取数据：

| 优先级 | 数据源 | 数据类型 | 获取方式 | 需要授权 |
|:---:|:---|:---|:---:|:---:|
| 1 | AkShare | 信托发行、收益率、基础统计 | API调用 | 否 |
| 2 | 用益信托网 | 产品详情、收益率排行 | 爬虫抓取 | 否 |
| 3 | **同花顺iFinD API** | 深度财务数据、行业指数、公司行情 | API调用 | **是** |
| 4 | 模拟数据 | 作为fallback | 本地 | 否 |

## 同花顺API配置

### 环境变量设置

```bash
export THS_ACCESS_TOKEN="your_access_token_here"
```

或在Python中设置：

```python
import os
os.environ['THS_ACCESS_TOKEN'] = 'your_access_token_here'
```

### 同花顺API支持的额外功能

| 功能 | 方法 | 说明 |
|:---|:---|:---|
| 信托公司财务数据 | `get_trust_company_financials()` | ROE、净利润、营收等 |
| 信托行业指数 | `get_trust_industry_index()` | 多元金融板块指数 |
| 头部公司行情 | `get_top_trust_companies()` | 主要信托母上市公司行情 |

### 示例：使用同花顺API获取深度数据

```python
from trust_data_adapter import get_data_provider

provider = get_data_provider()

# 获取平安信托财务数据
financials = provider.get_trust_company_financials('平安信托')
if financials:
    print(f"ROE: {financials['roe']}%")
    print(f"净利润: {financials['net_profit']}亿元")
    print(f"营收增长: {financials['revenue_growth']}%")

# 获取行业指数
index = provider.get_trust_industry_index()
if index:
    print(f"行业指数: {index['current_price']}")
    print(f"涨跌幅: {index['change']}%")

# 获取头部公司行情
companies = provider.get_top_trust_companies()
for c in companies[:5]:
    print(f"{c['company']}: {c['change_pct']}%")
```

## 支持的查询接口

### 获取信托产品列表

```python
products = provider.get_products(
    min_yield=7.0,           # 最低收益率
    max_duration=24,         # 最长期限（月）
    risk_level=['R2', 'R3'], # 风险等级
    trust_company='平安'      # 信托公司名称
)

for p in products:
    print(f"{p.product_name}: {p.expected_yield}%/{p.duration}月")
```

### 获取市场统计数据

```python
stats = provider.get_market_stats()
print(f"平均收益率: {stats.avg_yield}%")
print(f"发行规模: {stats.total_issuance}亿元")

# 分类型收益率
for type_name, yield_val in stats.yield_by_type.items():
    print(f"{type_name}: {yield_val}%")

# 分期限收益率
for duration, yield_val in stats.yield_by_duration.items():
    print(f"{duration}: {yield_val}%")
```

### 获取收益率曲线

```python
curve = provider.get_yield_curve()
print(curve)
# 输出:
#        期限    收益率
# 0    1年内    6.20
# 1    1-2年    6.85
# 2    2-3年    7.35
# 3   3年以上   7.80
```

## 数据模型

### TrustProductData

```python
@dataclass
class TrustProductData:
    product_code: str          # 产品代码
    product_name: str          # 产品名称
    trust_company: str         # 信托公司
    product_type: str          # 产品类型（集合/单一/财产权）
    investment_type: str       # 投资类型（固收/权益/混合/另类）
    expected_yield: float      # 预期收益率
    duration: int              # 期限（月）
    min_investment: float      # 起投金额（万元）
    issue_scale: float         # 发行规模（万元）
    issue_date: str            # 发行日期
    risk_level: str            # 风险等级（R1-R5）
    status: str                # 状态（在售/已成立/已清算）
    underlying_type: str       # 底层资产类型
```

### TrustMarketStats

```python
@dataclass
class TrustMarketStats:
    stat_date: str                    # 统计日期
    total_issuance: float             # 发行规模（亿元）
    product_count: int                # 产品数量
    avg_yield: float                  # 平均收益率
    yield_by_type: Dict[str, float]   # 分类型收益率
    yield_by_duration: Dict[str, float]  # 分期限收益率
```

### TrustCompanyFinancials

```python
@dataclass
class TrustCompanyFinancials:
    company: str         # 公司名称
    stock_code: str      # 股票代码
    roe: float           # ROE
    roe_adjusted: float  # 扣非ROE
    net_profit: float    # 净利润
    profit_growth: float # 净利润增长率
    revenue: float       # 营业收入
    revenue_growth: float # 营收增长率
    total_assets: float  # 总资产
    net_assets: float    # 净资产
    timestamp: str       # 时间戳
```

## 扩展新的数据源

```python
from trust_data_adapter import DataSourceAdapter

class MyDataSourceAdapter(DataSourceAdapter):
    def get_name(self) -> str:
        return "我的数据源"
    
    def is_available(self) -> bool:
        # 检查数据源是否可用
        return True
    
    def get_products(self, **filters) -> List[TrustProductData]:
        # 实现产品数据获取
        pass
    
    def get_market_stats(self) -> TrustMarketStats:
        # 实现市场统计获取
        pass

# 注册到数据提供器
provider = TrustDataProvider()
provider.adapters.insert(0, MyDataSourceAdapter())
```

## 故障排查

### 检查数据源状态

```python
info = provider.get_data_source_info()
for adapter in info['adapters']:
    print(f"{adapter['name']}: {'可用' if adapter['available'] else '不可用'}")
```

### 数据源不可用时的处理

数据对接层会自动fallback到下一个可用数据源，最终会使用模拟数据保证服务可用性。

## 更新日志

### v1.1.0 (2026-03-20)
- 新增同花顺iFinD API支持
- 支持信托公司财务数据查询
- 支持信托行业指数查询
- 支持头部信托公司行情查询

### v1.0.0 (2026-03-20)
- 初始版本发布
- 支持AkShare、用益信托网、模拟数据三个数据源
- 提供产品查询、市场统计、收益率曲线接口
