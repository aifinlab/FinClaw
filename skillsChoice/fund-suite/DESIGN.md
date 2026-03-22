# FinClaw 基金Skills套件 - 设计文档

## 项目概述

基于OpenClaw框架开发10个高阶基金Skills，覆盖基金投研全流程，支持A股、港股、美股基金，提供专业的筛选、配置、分析、监控能力。

---

## 10个基金Skills设计

### 1. fund-screener (基金筛选器)
**定位**: 智能基金筛选与评级
**核心功能**:
- 多维度基金筛选（收益/风险/规模/费率）
- 基金评级打分（五星评级体系）
- 基金经理能力评估
- 同类基金排名对比
- 智能推荐算法

**输入**: 筛选条件（收益率、风险等级、投资类型等）
**输出**: 符合条件的基金列表 + 评级报告

**数据源**: 
- 同花顺iFinD API（基金净值、规模）
- AkShare（基金基本信息）
- 天天基金网（费率数据）

---

### 2. fund-portfolio-allocation (基金组合配置)
**定位**: 智能基金组合构建与优化
**核心功能**:
- 战略资产配置（SAA）
- 战术资产配置（TAA）
- Markowitz均值方差优化
- 风险平价配置
- 目标日期/目标风险策略
- 再平衡策略

**输入**: 投资目标、风险承受度、投资期限、初始资金
**输出**: 组合配置方案 + 预期收益风险

**算法**:
- Black-Litterman模型
- 风险平价算法
- 最大回撤控制

---

### 3. fund-sip-planner (基金定投规划)
**定位**: 智能定投策略设计与回测
**核心功能**:
- 定投金额规划（固定/智能/估值）
- 定投频率优化（日/周/月）
- 智能定投策略（均线/估值/趋势）
- 定投回测分析
- 止盈止损策略
- 定投收益计算器

**输入**: 目标金额、定投周期、风险偏好、基金标的
**输出**: 定投方案 + 回测报告

**策略**:
- 均线定投（偏离度触发）
- 估值定投（PE/PB分位）
- 趋势定投（技术指标）

---

### 4. fund-risk-analyzer (基金风险分析)
**定位**: 基金风险识别与量化分析
**核心功能**:
- VaR/CVaR计算
- 最大回撤分析
- 波动率分解
- Beta/Alpha计算
- 夏普比率/索提诺比率
- 下行风险分析
- 尾部风险预警

**输入**: 基金代码、分析周期、置信度
**输出**: 风险分析报告 + 风险指标

**模型**:
- 历史模拟法VaR
- 蒙特卡洛模拟
- GARCH波动率模型

---

### 5. fund-attribution-analysis (基金业绩归因)
**定位**: 基金收益来源分解
**核心功能**:
- Brinson归因模型
- 风格归因分析（Barra模型）
- 行业配置归因
- 个股选择归因
- 交互效应分析
- 多期归因分析

**输入**: 基金持仓、基准指数、分析周期
**输出**: 归因分析报告 + 各因子贡献

**归因维度**:
- 资产配置效应
- 行业选择效应
- 个股选择效应
- 交互效应

---

### 6. fund-holding-analyzer (基金持仓分析)
**定位**: 基金持仓深度分析
**核心功能**:
- 持仓集中度分析
- 行业分布分析
- 重仓股分析
- 持仓变化追踪
- 相似基金发现
- 抱团股识别
- 估值分析（持仓PE/PB）

**输入**: 基金代码、对比基金
**输出**: 持仓分析报告 + 可视化图表

**分析维度**:
- 前十大重仓占比
- 行业偏离度
- 持仓换手率
- 估值分位数

---

### 7. fund-rebalance-advisor (基金换仓建议)
**定位**: 基金组合再平衡与调仓建议
**核心功能**:
- 组合偏离度检测
- 再平衡时机建议
- 换仓标的推荐
- 交易成本优化
- 税务影响分析
- 调仓路径规划
- 模拟调仓回测

**输入**: 当前组合、目标配置、约束条件
**输出**: 换仓建议方案 + 执行计划

**触发条件**:
- 偏离度阈值（5%/10%）
- 定期再平衡（季度/年度）
- 市场极端情况

---

### 8. fund-market-research (基金市场研究)
**定位**: 基金市场全景研究与趋势分析
**核心功能**:
- 市场规模统计
- 新发基金追踪
- 资金流向分析
- 热门板块追踪
- 基金收益率曲线
- 市场情绪指标
- 基金发行日历

**输入**: 市场维度、时间范围
**输出**: 市场研究报告 + 数据可视化

**研究维度**:
- 权益/固收/商品基金分布
- 规模变化趋势
- 收益分布统计

---

### 9. fund-tax-optimizer (基金税务优化)
**定位**: 基金投资税务优化策略
**核心功能**:
- 赎回税率计算
- 持有期优化建议
- 分红再投策略
- 税损收割（Tax Loss Harvesting）
- 申赎时点优化
- 不同类型基金税负对比
- 年度税务规划

**输入**: 持仓基金、持有期、收益情况、税率
**输出**: 税务优化方案 + 节税测算

**规则**:
- A股基金：持有<7天1.5%，<30天0.75%，>2年0%
- 港股基金：QDII税率
- 货币基金：免税

---

### 10. fund-monitor (基金智能监控)
**定位**: 基金组合实时监控与预警
**核心功能**:
- 净值变动监控
- 收益率预警
- 回撤预警
- 规模异动监控
- 基金经理变更提醒
- 持仓重大变化提醒
- 市场事件关联分析
- 智能报告生成

**输入**: 监控基金列表、预警阈值
**输出**: 实时预警 + 监控报告

**预警类型**:
- 收益率偏离
- 最大回撤触发
- 规模大幅变化
- 持仓集中度变化

---

## 技术架构

### 数据层
```
data/
├── fund_data_adapter.py      # 统一数据接口
├── ths_fund_adapter.py       # 同花顺基金API
├── eastmoney_fund.py         # 东方财富基金数据
├── tiantian_fund.py          # 天天基金网数据
└── fund_cache.py             # 数据缓存管理
```

### Skills目录结构
```
finclaw/skills/fund-suite/
├── fund-screener/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── screener.py
│   └── evals/
├── fund-portfolio-allocation/
├── fund-sip-planner/
├── fund-risk-analyzer/
├── fund-attribution-analysis/
├── fund-holding-analyzer/
├── fund-rebalance-advisor/
├── fund-market-research/
├── fund-tax-optimizer/
└── fund-monitor/
```

### 统一数据模型
```python
@dataclass
class FundData:
    fund_code: str           # 基金代码
    fund_name: str           # 基金名称
    fund_type: str           # 基金类型
    nav: float              # 最新净值
    nav_date: str           # 净值日期
    manager: str            # 基金经理
    company: str            # 基金公司
    scale: float            # 基金规模
    expense_ratio: float    # 管理费率
    return_1y: float        # 近1年收益
    return_3y: float        # 近3年收益
    volatility: float       # 波动率
    sharpe_ratio: float     # 夏普比率
    max_drawdown: float     # 最大回撤
    
@dataclass
class FundPortfolio:
    portfolio_id: str
    holdings: List[FundHolding]
    total_value: float
    expected_return: float
    risk_level: str
```

---

## 数据源规划

| 数据源 | 数据类型 | 覆盖范围 | 更新频率 |
|:---|:---|:---|:---|
| 同花顺iFinD | 净值/规模/持仓 | A股基金 | 日度 |
| AkShare | 基本信息/费率 | A股基金 | 日度 |
| 天天基金 | 费率/评级 | A股基金 | 日度 |
| Wind/Choice | 深度数据 | 全市场 | 日度 |
| Yahoo Finance | 海外基金 | QDII | 日度 |

---

## 开发计划

### Phase 1: 核心Skills (Week 1-2)
1. fund-screener - 基金筛选器
2. fund-risk-analyzer - 风险分析
3. fund-market-research - 市场研究

### Phase 2: 配置Skills (Week 3-4)
4. fund-portfolio-allocation - 组合配置
5. fund-sip-planner - 定投规划
6. fund-rebalance-advisor - 换仓建议

### Phase 3: 分析Skills (Week 5-6)
7. fund-attribution-analysis - 业绩归因
8. fund-holding-analyzer - 持仓分析
9. fund-tax-optimizer - 税务优化

### Phase 4: 监控Skills (Week 7)
10. fund-monitor - 智能监控

---

## 预期输出示例

### fund-screener 输出示例
```
筛选条件: 股票型、规模>10亿、近1年收益>10%、夏普>1.0

排名 基金名称        近1年收益  夏普比率  规模(亿)  评级
1    富国天惠成长    25.3%     1.45      156.8    ⭐⭐⭐⭐⭐
2    易方达蓝筹精选  22.1%     1.38      234.5    ⭐⭐⭐⭐⭐
3    中欧时代先锋    18.7%     1.22       89.3    ⭐⭐⭐⭐
```

### fund-portfolio-allocation 输出示例
```
投资目标: 稳健增长
风险等级: R3
初始资金: 100万

配置方案:
├── 股票型基金: 60% (¥60万)
│   ├── 富国天惠: 25%
│   ├── 易方达蓝筹: 20%
│   └── 中欧时代: 15%
├── 债券型基金: 30% (¥30万)
│   └── 招商产业债: 30%
└── 货币基金: 10% (¥10万)
    └── 天弘余额宝: 10%

预期收益: 8.5% | 预期波动: 12% | 最大回撤: -15%
```

---

*设计完成时间: 2026-03-21*
*架构师: FinClaw 金融机器人*
