# FinClaw 信托模块文档

> 文档创建时间: 2026-03-20
> 作者: FinClaw 开发团队
> 版本: v1.0.0

---

## 一、项目概述

### 1.1 背景
信托行业是中国金融体系的重要组成部分，涉及财富管理、资产配置、风险隔离等多个专业领域。FinClaw 信托模块旨在为信托行业提供一站式的智能分析工具，覆盖产品设计、投资决策、风险管理、合规审查等全流程。

### 1.2 目标
- 构建中国首个开源信托智能分析工具套件
- 覆盖信托业务全流程：研究 → 分析 → 决策 → 监控
- 整合多源数据：同花顺iFinD API、AkShare、用益信托网等
- 提供专业级分析能力：VaR计算、资产配置优化、压力测试等

### 1.3 技术栈
- **语言**: Python 3.12+
- **数据处理**: Pandas, NumPy
- **金融计算**: SciPy, numpy-financial
- **数据可视化**: Matplotlib, Plotly
- **数据来源**: 同花顺iFinD API, AkShare, 用益信托网

---

## 二、模块架构

```
finclaw/skills/trust-suite/
├── data/                          # 数据对接层
│   ├── trust_data_adapter.py     # 统一数据接口
│   ├── ths_adapter.py            # 同花顺API适配器
│   ├── init_data.py              # 数据初始化
│   └── README.md                 # 数据层说明
│
├── trust-product-analyzer/        # 1. 产品分析器
│   └── scripts/main_v2.py
├── trust-asset-allocation/        # 2. 资产配置
│   └── scripts/main.py
├── trust-risk-manager/            # 3. 风险管理
│   └── scripts/main.py
├── trust-compliance-checker/      # 4. 合规审查
│   └── scripts/main.py
├── trust-income-calculator/       # 5. 收益计算
│   └── scripts/main.py
├── family-trust-designer/         # 6. 家族信托
│   └── scripts/main.py
├── charity-trust-manager/         # 7. 慈善信托
│   └── scripts/main.py
├── trust-valuation-engine/        # 8. 估值引擎
│   └── scripts/main.py
├── trust-post-investment-monitor/ # 9. 投后监控
│   └── scripts/main.py
└── trust-market-research/         # 10. 市场研究
    └── scripts/main.py
```

---

## 三、功能详情

### 3.1 信托产品综合分析器 (trust-product-analyzer)

**功能定位**: 信托产品的"体检报告"

**核心能力**:
| 功能 | 说明 |
|:---|:---|
| 产品筛选 | 按收益、期限、风险等级、发行机构筛选 |
| 风险评估 | 信用风险、市场风险、流动性风险评分 |
| 竞品对比 | 同类产品横向对比分析 |
| 合规检查 | 嵌套层数、关联交易、合格投资者 |

**代码示例**:
```python
from trust_data_adapter import get_data_provider

provider = get_data_provider()
products = provider.get_products(
    min_yield=7.0,      # 最低7%收益
    max_duration=24,    # 最长24个月
    risk_levels=['R2', 'R3']
)

for p in products:
    print(f"{p.product_name}: {p.expected_yield}%/{p.duration}月")
```

**输出示例**:
```
产品名称: 中港稳健1号集合资金信托计划
发行机构: 中港信托有限公司
预期收益: 7.2%/18月
风险评分: 77/100 (中等风险)
信用风险: 75分 - 中低风险
市场风险: 70分 - 中等风险
流动性风险: 85分 - 低风险
合规检查: ✅ 通过
```

---

### 3.2 信托资产配置优化 (trust-asset-allocation)

**功能定位**: 智能资产配置建议

**算法支持**:
1. **Markowitz均值方差优化**: 风险收益平衡
2. **风险平价**: 各资产风险贡献相等
3. **Black-Litterman**: 融合市场观点
4. **目标日期策略**: 随期限自动调整

**代码示例**:
```python
from trust_asset_allocation.scripts.main import AssetAllocator

allocator = AssetAllocator()
result = allocator.optimize_markowitz(
    assets=['中港稳健1号', '平安优享2号', '中建城市3号'],
    returns=[0.072, 0.080, 0.068],
    risks=[0.05, 0.08, 0.04],
    correlations=[[1, 0.3, 0.5], [0.3, 1, 0.2], [0.5, 0.2, 1]]
)

print(f"预期收益: {result['expected_return']*100:.2f}%")
print(f"组合风险: {result['portfolio_risk']*100:.2f}%")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
```

**输出示例**:
```
预期收益: 7.54%
组合风险: 4.85%
夏普比率: 1.32
权重分配:
  中港稳健1号: 45.0%
  平安优享2号: 30.0%
  中建城市3号: 25.0%
```

---

### 3.3 信托风险管理 (trust-risk-manager)

**功能定位**: 全面风险识别与监控

**风险指标**:
- **VaR (风险价值)**: 95%/99%置信度
- **CVaR (条件风险价值)**: 尾部风险
- **久期分析**: 利率敏感度
- **信用风险敞口**: 集中度分析

**压力测试场景**:
| 场景 | 冲击幅度 | 预期损失 |
|:---|:---:|---:|
| 利率上升 | 200bp | ¥1,250万 |
| 信用利差扩大 | 300bp | ¥2,800万 |
| 流动性枯竭 | 极端情况 | ¥4,500万 |

**代码示例**:
```python
from trust_risk_manager.scripts.main import TrustRiskManager

risk_mgr = TrustRiskManager()

# VaR计算
var_result = risk_mgr.calculate_var(
    portfolio_value=100000000,  # 1亿组合
    confidence_level=0.95,
    volatility=0.15
)
print(f"95% VaR: ¥{var_result['var']/1e4:.2f}万")

# 压力测试
stress = risk_mgr.stress_test(scenarios=[
    {'name': '利率上升200bp', 'rate_shock': 0.02}
])
```

---

### 3.4 信托合规审查 (trust-compliance-checker)

**功能定位**: 自动化合规检查

**检查项**:
| 检查项 | 说明 | 标准 |
|:---|:---|:---|
| 合格投资者 | 起投金额检查 | ≥300万 |
| 嵌套层数 | 穿透检查 | ≤2层 |
| 投资限制 | 监管要求 | 符合资管新规 |
| 关联交易 | 关联方识别 | 标识+披露 |
| 投资者适当性 | 风险匹配 | 等级匹配 |

---

### 3.5 信托收益计算 (trust-income-calculator)

**功能定位**: 收益测算与税务分析

**计算功能**:
- **IRR/XIRR**: 内部收益率
- **预期收益**: 按不同付息方式
- **税务影响**: 增值税、所得税

**代码示例**:
```python
from trust_income_calculator.scripts.main import IncomeCalculator

calc = IncomeCalculator()

# IRR计算
irr = calc.calculate_irr(
    cashflows=[-10000000, 500000, 500000, 500000, 10500000]
)
print(f"IRR: {irr['irr']*100:.2f}%")

# 预期收益
yield_calc = calc.calculate_expected_yield(
    principal=10000000,
    annual_yield=0.072,
    duration_months=18,
    distribution='quarterly'
)
print(f"总收益: ¥{yield_calc['total_income']:,.0f}")
```

---

### 3.6 家族信托架构设计 (family-trust-designer)

**功能定位**: 财富传承方案设计

**设计要素**:
- 传承代数规划 (2-5代)
- 分配方案设计 (比例/条件)
- 治理架构设计 (保护人/顾问)
- 税务优化策略

**示例方案**:
```
传承代数: 3代
分配方案:
  第一代: 20% - 养老保障
  第二代: 50% - 事业发展
  第三代: 30% - 教育基金
治理架构:
  保护人: 家族委员会
  顾问: 专业信托公司
  分配决策: 3人决策小组
```

---

### 3.7-3.10 其他Skills

| Skill | 核心功能 |
|:---|:---|
| **慈善信托管理器** | 公益项目筛选、资金监管、税务优化 |
| **信托估值引擎** | 非标债权估值、股权估值、NAV计算 |
| **投后监控** | 预警指标、风险事件、处置建议 |
| **市场研究** | 行业统计、收益率走势、竞品分析 |

---

## 四、数据对接层

### 4.1 架构设计

```
┌─────────────────────────────────────────┐
│         TrustDataProvider               │
│         (统一数据接口)                   │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ 同花顺   │   │ AkShare │   │ 用益信托 │
│ iFinD   │   │ (开源)  │   │ 网爬虫  │
└─────────┘   └─────────┘   └─────────┘
    │               │               │
    └───────────────┴───────────────┘
                    │
            ┌─────────────┐
            │  模拟数据    │
            │ (Fallback) │
            └─────────────┘
```

### 4.2 数据源详情

| 数据源 | 状态 | 数据类型 | 更新频率 |
|:---|:---:|:---|:---|
| **同花顺iFinD API** | ✅ 已对接 | 实时行情、财务数据 | 实时 |
| **AkShare** | ✅ 就绪 | 宏观数据、行业统计 | 日更 |
| **用益信托网** | ✅ 就绪 | 产品数据、市场统计 | 日更 |
| **模拟数据** | ✅ 就绪 | 演示/测试 | - |

### 4.3 同花顺API对接

**关键配置**:
```python
# API地址
THS_BASE_URL = "https://quantapi.51ifind.com/api/v1"

# 认证方式
headers = {'access_token': token}

# 请求方式
requests.post(url, json=data)

# 股票代码格式
codes = ['600519.SH', '000001.SZ']  # 带后缀
```

**已实现功能**:
- ✅ 实时行情查询 (10家头部信托公司)
- ✅ 股票代码格式转换
- ✅ 自动缓存机制 (30分钟)
- ⚠️ 财务数据 (待指标代码确认)
- ⚠️ 行业指数 (待代码确认)

---

## 五、信托公司代码映射

```python
TRUST_COMPANY_CODES = {
    '平安信托': '000001.SZ',  # 平安银行关联
    '中航信托': '600705.SH',  # 中航产融
    '五矿信托': '600390.SH',  # 五矿资本
    '中粮信托': '000423.SZ',  # 中粮资本关联
    '中融信托': '600291.SH',  # ST西水
    '爱建信托': '600643.SH',  # 爱建集团
    '陕国投':   '000563.SZ',  # 陕国投A
    '安信信托': '600816.SH',  # 建元信托
    '江苏信托': '000544.SZ',  # 中原高速关联
    '昆仑信托': '000617.SZ',  # 中油资本
}
```

---

## 六、使用指南

### 6.1 环境配置

```bash
# 安装依赖
pip install pandas numpy scipy requests beautifulsoup4

# 配置同花顺Token (可选)
export THS_ACCESS_TOKEN="your_token_here"
```

### 6.2 快速开始

```bash
# 运行完整演示
cd finclaw/skills/trust-suite
python3 demo_all_skills.py

# 产品分析
cd trust-product-analyzer/scripts
python3 main_v2.py --action screen --min-yield 7.0

# 数据对接层测试
cd data
python3 init_data.py
```

### 6.3 API使用

```python
from data.trust_data_adapter import get_data_provider

# 获取数据提供者
provider = get_data_provider()

# 获取产品数据
products = provider.get_products(min_yield=7.0, max_duration=24)

# 获取市场统计
stats = provider.get_market_stats()

# 获取头部公司行情
companies = provider.get_top_trust_companies()
```

---

## 七、项目统计

### 7.1 代码规模

| 类别 | 文件数 | 代码行数 |
|:---|:---:|:---:|
| 数据对接层 | 4 | ~900 |
| 10个Skills | 10 | ~3,000 |
| 测试/演示 | 3 | ~150 |
| 文档 | 4 | ~500 |
| **总计** | **21** | **~4,550** |

### 7.2 开发时间线

| 日期 | 里程碑 |
|:---|:---|
| 2026-03-15 | 信托Skills规划启动 |
| 2026-03-18 | 10个Skills框架完成 |
| 2026-03-20 | 同花顺API对接成功 |
| 2026-03-20 | 完整测试通过 |

---

## 八、后续优化

### 8.1 短期 (1-2周)
- [ ] 确认同花顺财务指标代码
- [ ] 确认信托行业指数代码
- [ ] 完善单元测试覆盖

### 8.2 中期 (1-2月)
- [ ] 接入更多信托公司行情
- [ ] 开发Web可视化界面
- [ ] 添加机器学习预测模型

### 8.3 长期 (3-6月)
- [ ] 支持更多数据源 (Wind/Choice)
- [ ] 构建信托知识图谱
- [ ] 智能投顾功能

---

## 九、相关文档

- `DATA_SOURCES.md` - 数据对接层详细说明
- `THS_API_SUCCESS_REPORT.md` - 同花顺API对接报告
- `SKILL.md` - 各Skill使用说明
- `demo_all_skills.py` - 完整功能演示

---

## 十、联系方式

- **项目**: FinClaw - 上海财经大学金融研究CLI工具
- **维护**: FinClaw 开发团队
- **更新**: 2026-03-20

---

*本文档由 FinClaw 自动生成*
