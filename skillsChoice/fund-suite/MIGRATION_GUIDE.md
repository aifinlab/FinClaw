# Fund Suite 真实数据迁移指南

## 已完成迁移

| Skill | v2文件 | 状态 |
|:---|:---|:---:|
| fund-screener | fund_screener_v2.py | ✅ 已测试 |
| fund-portfolio-allocation | fund_portfolio_allocation_v2.py | ✅ 已测试 |

## 待迁移Skills

| Skill | 优先级 | 说明 |
|:---|:---:|:---|
| fund-sip-planner | 高 | 定投规划 |
| fund-rebalance-advisor | 高 | 换仓建议 |
| fund-monitor | 高 | 组合监控 |
| fund-attribution-analysis | 中 | 收益归因 |
| fund-holding-analyzer | 中 | 持仓分析 |
| fund-tax-optimizer | 中 | 税务优化 |
| fund-market-research | 低 | 市场研究 |
| fund-risk-analyzer | 低 | 风险分析 |

## 迁移步骤

### 1. 添加导入
```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False
    print(f"警告：数据适配器未加载: {e}")
```

### 2. 初始化适配器
```python
def __init__(self, use_real_data: bool = True):
    self.data_adapter = None
    self.data_source = "模拟数据"
    
    if use_real_data and DATA_ADAPTER_AVAILABLE:
        self._init_data_adapter()
    
    self._load_data()

def _init_data_adapter(self):
    try:
        self.data_adapter = get_fund_adapter(prefer_ths=False)
        self.data_source = self.data_adapter.get_data_source()
        print(f"✅ 数据源: {self.data_source}")
    except Exception as e:
        print(f"⚠️ 数据适配器初始化失败: {e}")
```

### 3. 加载真实数据
```python
def _load_data(self):
    if self.data_adapter:
        try:
            self._load_real_data()
            if self.fund_data:
                print(f"✅ 已加载真实数据")
                return
        except Exception as e:
            print(f"⚠️ 真实数据加载失败: {e}")
    
    self._load_sample_data()
```

### 4. 使用数据适配器
```python
def _load_real_data(self):
    # 基金搜索
    funds = self.data_adapter.search_funds("易方达")
    
    # 获取净值
    navs = self.data_adapter.get_fund_nav("005827", days=30)
    
    # 获取业绩
    perf = self.data_adapter.get_fund_performance("005827")
    
    # 获取持仓
    holdings = self.data_adapter.get_fund_holdings("005827", quarter="2024Q4")
```

## 数据适配器API

```python
from fund_data_adapter import get_fund_adapter

adapter = get_fund_adapter(prefer_ths=False)

# 搜索基金
funds = adapter.search_funds(keyword: str) -> List[FundBasicInfo]

# 获取净值历史  
navs = adapter.get_fund_nav(fund_code: str, days: int) -> List[FundNetValue]

# 获取业绩
perf = adapter.get_fund_performance(fund_code: str) -> FundPerformance

# 获取持仓
holdings = adapter.get_fund_holdings(fund_code: str, quarter: str) -> List[FundHolding]
```

## 数据结构

```python
@dataclass
class FundBasicInfo:
    fund_code: str
    fund_name: str
    fund_type: str
    nav: float
    acc_nav: float
    update_date: str

@dataclass
class FundNetValue:
    fund_code: str
    date: str
    nav: float
    acc_nav: float
    daily_return: float

@dataclass
class FundPerformance:
    fund_code: str
    return_1m: float
    return_3m: float
    return_6m: float
    return_1y: float
    return_2y: float
    return_3y: float
    return_ytd: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float

@dataclass
class FundHolding:
    fund_code: str
    stock_code: str
    stock_name: str
    weight: float
    sector: str
```

## 一键迁移脚本

```bash
# 复制v1为v2
cp fund_screener.py fund_screener_v2.py
cp fund_portfolio_allocation.py fund_portfolio_allocation_v2.py

# 添加数据适配器导入和初始化代码
# 修改数据加载逻辑
# 测试运行
python3 fund_xxx_v2.py
```

## 注意事项

1. **数据源降级**: 真实数据获取失败时自动使用模拟数据
2. **缓存机制**: 适配器内置5分钟缓存，减少API调用
3. **同花顺iFinD**: 设置 `THS_ACCESS_TOKEN` 环境变量后可使用
4. **数据延迟**: AkShare数据为T+1，非实时
