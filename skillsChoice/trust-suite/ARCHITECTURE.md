# 信托领域 Skills 架构设计

## 一、信托业务全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        信托业务生态全景                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  【资金端】          【资产端】            【服务端】              │
│  ├─ 产品发行         ├─ 资产配置          ├─ 合规审查             │
│  ├─ 合格投资者       ├─ 投资管理          ├─ 风险管理             │
│  ├─ 募集管理         ├─ 投后监控          ├─ 估值核算             │
│  └─ 收益分配         └─ 资产处置          └─ 信息披露             │
│                                                                  │
│  【特色业务】                                                     │
│  ├─ 家族信托（财富传承、资产隔离）                                 │
│  ├─ 慈善信托（公益慈善、税务筹划）                                 │
│  └─ 资产证券化（ABS、REITs）                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 二、10个信托Skills设计矩阵

| # | Skill名称 | 核心功能 | 业务场景 | 技术栈 |
|:---:|---|---|---|---|
| 1 | `trust-product-analyzer` | 信托产品综合分析 | 产品筛选、竞品对比、尽职调查 | Python + 爬虫 + NLP |
| 2 | `trust-asset-allocation` | 信托资产配置优化 | 战略/战术资产配置、再平衡 | Python + 优化算法 |
| 3 | `trust-risk-manager` | 信托风险管理与预警 | 信用/市场/流动性风险监控 | Python + 风险模型 |
| 4 | `trust-compliance-checker` | 信托合规审查 | 合格投资者、嵌套层数、投资限制 | Python + 规则引擎 |
| 5 | `trust-income-calculator` | 信托收益计算与分配 | 预期收益、实际分配、 IRR计算 | Python + 金融计算 |
| 6 | `family-trust-designer` | 家族信托架构设计 | 传承方案、税务优化、资产隔离 | Python + 方案生成 |
| 7 | `charity-trust-manager` | 慈善信托管理 | 公益项目、资金监管、税务优惠 | Python + 公益数据 |
| 8 | `trust-valuation-engine` | 信托资产估值引擎 | 非标估值、净值计算、减值测试 | Python + 估值模型 |
| 9 | `trust-post-investment-monitor` | 信托投后监控 | 预警指标、处置建议、定期报告 | Python + 监控引擎 |
| 10 | `trust-market-research` | 信托市场研究 | 行业数据、发行统计、趋势分析 | Python + 数据可视化 |

## 三、数据架构设计

### 3.1 数据源整合

```python
# 信托数据分层架构
TRUST_DATA_SOURCES = {
    # 公开数据源
    "public": {
        "chinatrust": "中国信托登记有限责任公司",
        "cbirc": "国家金融监督管理总局",
        "fundapi": "用益信托网",
        "chinabond": "中国债券信息网",
        "stock_exchange": "沪深交易所公告"
    },
    # 内部数据源（需接入）
    "internal": {
        "ta_system": "TA登记过户系统",
        "valuation_system": "估值核算系统",
        "risk_system": "风险管理系统",
        "compliance_system": "合规管理系统"
    },
    # 第三方数据源
    "third_party": {
        "wind": "万得",
        "choice": "东方财富Choice",
        "ifind": "同花顺iFinD"
    }
}
```

### 3.2 核心数据模型

```python
# 信托产品核心模型
class TrustProduct:
    - product_code: str          # 产品代码
    - product_name: str          # 产品名称
    - trust_type: Enum           # 信托类型（集合/单一/财产权）
    - investment_type: Enum      # 投资类型（固收/权益/混合/另类）
    - risk_level: int            # 风险等级 R1-R5
    - min_investment: Decimal    # 起投金额
    - duration: int              # 期限（月）
    - expected_yield: Decimal    # 预期收益率
    - distribution_way: Enum     # 分配方式
    - underlying_assets: List    # 底层资产
    - risk_measures: Dict        # 风控措施
    - compliance_status: bool    # 合规状态

# 信托资产组合模型
class TrustPortfolio:
    - portfolio_id: str
    - asset_allocation: Dict     # 资产配置比例
    - duration_matching: Dict    # 久期匹配
    - credit_exposure: Dict      # 信用敞口
    - liquidity_profile: Dict    # 流动性分析
    - performance_attribution: Dict # 业绩归因
```

## 四、Skills 技术规范

### 4.1 目录结构规范

```
skills/
├── trust-product-analyzer/
│   ├── SKILL.md              # Skill说明文档
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── main.py           # 主入口
│   │   ├── product_fetcher.py    # 数据采集
│   │   ├── product_analyzer.py   # 分析引擎
│   │   └── report_generator.py   # 报告生成
│   ├── requirements.txt      # 依赖包
│   └── LICENSE               # 许可证
├── trust-asset-allocation/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── main.py
│   │   ├── optimizer.py      # 优化算法
│   │   ├── constraints.py    # 约束条件
│   │   └── backtest.py       # 回测模块
│   ├── requirements.txt
│   └── LICENSE
└── ... (其他8个Skills)
```

### 4.2 输入输出规范

```python
# 统一输入格式
{
    "action": "analyze",        # 操作类型
    "product_code": "",         # 产品代码（可选）
    "query": "",                # 自然语言查询
    "filters": {},              # 筛选条件
    "output_format": "json"     # 输出格式
}

# 统一输出格式
{
    "status": "success",
    "data": {},
    "metadata": {
        "source": "trust-product-analyzer",
        "version": "1.0.0",
        "timestamp": "2026-03-20T14:00:00Z"
    },
    "confidence": 0.95,
    "disclaimer": "本分析仅供参考，不构成投资建议"
}
```

## 五、核心功能模块设计

### 5.1 信托产品智能分析引擎

```python
class TrustAnalysisEngine:
    """
    信托产品综合分析引擎
    
    功能：
    1. 产品信息抓取与解析
    2. 风险评级与评估
    3. 收益测算与对比
    4. 合规性检查
    5. 竞品对比分析
    """
    
    def analyze_product(self, product_code: str) -> Dict:
        pass
    
    def compare_products(self, product_codes: List[str]) -> Dict:
        pass
    
    def risk_assessment(self, product: TrustProduct) -> RiskReport:
        pass
```

### 5.2 资产配置优化引擎

```python
class AssetAllocationOptimizer:
    """
    信托资产配置优化引擎
    
    算法：
    1. 均值-方差优化（Markowitz）
    2. 风险平价模型
    3. Black-Litterman模型
    4. 目标日期策略
    """
    
    def optimize(self, 
                 target_return: float,
                 risk_tolerance: float,
                 constraints: Dict) -> AllocationResult:
        pass
```

### 5.3 风险预警引擎

```python
class RiskMonitoringEngine:
    """
    信托风险监控预警引擎
    
    监控维度：
    1. 信用风险（融资主体、担保措施、偿债能力）
    2. 市场风险（利率、汇率、商品价格）
    3. 流动性风险（赎回压力、资产变现能力）
    4. 操作风险（流程合规、系统安全）
    """
    
    def monitor_credit_risk(self, portfolio: TrustPortfolio) -> RiskReport:
        pass
    
    def generate_early_warning(self, threshold: float) -> List[Warning]:
        pass
```

## 六、开发路线图

### Phase 1: 核心基础设施（Week 1）
- [ ] 信托数据模型定义
- [ ] 公共数据抓取模块
- [ ] 统一输出格式规范

### Phase 2: 基础Skills开发（Week 2-3）
- [ ] trust-product-analyzer
- [ ] trust-income-calculator
- [ ] trust-compliance-checker

### Phase 3: 进阶Skills开发（Week 4-5）
- [ ] trust-risk-manager
- [ ] trust-valuation-engine
- [ ] trust-asset-allocation

### Phase 4: 特色业务Skills（Week 6-7）
- [ ] family-trust-designer
- [ ] charity-trust-manager
- [ ] trust-post-investment-monitor

### Phase 5: 市场研究Skill（Week 8）
- [ ] trust-market-research

## 七、使用场景示例

### 场景1：理财师筛选信托产品

```
用户：帮我筛选预期收益7%以上、期限2年内、R3风险等级的固收类信托产品

→ trust-product-analyzer
→ 输出：符合条件的产品列表、风险分析、收益测算
```

### 场景2：信托经理进行资产配置

```
用户：为一个家族信托客户设计资产配置方案，目标年化收益8%，最大回撤不超过15%

→ family-trust-designer（架构设计）
→ trust-asset-allocation（组合优化）
→ trust-risk-manager（风险校验）
```

### 场景3：合规部门审查

```
用户：审查XX信托计划是否涉及多层嵌套、是否穿透识别了最终投资者

→ trust-compliance-checker
→ 输出：嵌套层级图、合规性报告、整改建议
```

## 八、技术选型

| 组件 | 技术栈 | 说明 |
|---|---|---|
| 数据采集 | requests + aiohttp + BeautifulSoup | 异步抓取 |
| 数据处理 | pandas + numpy | 金融计算 |
| 优化算法 | scipy.optimize + cvxpy | 凸优化 |
| 风险评估 | pyfolio + empyrical | 风险指标 |
| 报告生成 | jinja2 + markdown | 模板引擎 |
| 数据可视化 | matplotlib + plotly | 图表生成 |
| 规则引擎 | durable-rules | 合规检查 |

---

**设计完成时间**: 2026-03-20
**版本**: v1.0.0
**架构师**: FinClaw Team
