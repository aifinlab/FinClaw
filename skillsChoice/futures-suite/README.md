# 期货套件 (Futures Suite) - 10个高阶期货Skills

## 概述

期货套件包含10个专业的期货分析Skills，覆盖期货市场概览、成交持仓分析、保证金计算、套利分析、风险分析、商品/金融期货专项分析、持仓追踪、交割分析、宏观相关性分析等多个维度。全部使用真实数据源。

---

## 10个Skills一览

| # | Skill名称 | 核心功能 | 数据源 |
|:---:|---|---|---|
| 1 | **futures-market-overview** | 期货市场概览（成交持仓、各品种活跃度） | AkShare、上期所、大商所、郑商所、中金所 |
| 2 | **futures-volume-analyzer** | 成交持仓分析（量价关系、资金流向） | AkShare、交易所 |
| 3 | **futures-margin-calculator** | 保证金计算（交易所/期货公司保证金率） | 交易所官方标准 |
| 4 | **futures-arbitrage-analyzer** | 套利分析（跨期/跨品种/期现套利） | AkShare |
| 5 | **futures-risk-analyzer** | 风险分析（波动率、VaR、最大回撤） | AkShare |
| 6 | **commodity-futures-analyzer** | 商品期货分析（板块、产业链、季节性） | AkShare、交易所 |
| 7 | **financial-futures-analyzer** | 金融期货分析（股指/国债期货基差） | AkShare、中金所 |
| 8 | **futures-position-tracker** | 持仓追踪（期货公司持仓排名、主力动向） | 交易所持仓数据 |
| 9 | **futures-delivery-analyzer** | 交割分析（交割成本、仓单、逼仓风险） | 交易所交割数据 |
| 10 | **futures-macro-correlation** | 宏观相关性（期货与PMI/CPI/利率/汇率） | AkShare宏观数据 |

---

## 支持的交易所

| 交易所 | 代码 | 主要品种 |
|--------|------|----------|
| 上海期货交易所 | SHFE | 铜、铝、锌、黄金、白银、螺纹钢、原油 |
| 大连商品交易所 | DCE | 豆粕、豆油、铁矿石、焦炭、塑料 |
| 郑州商品交易所 | CZCE | 白糖、棉花、PTA、甲醇、玻璃 |
| 中国金融期货交易所 | CFFEX | 股指、国债期货 |
| 上海国际能源交易中心 | INE | 原油期货 |

---

## 支持的品种分类

### 有色金属
铜(CU)、铝(AL)、锌(ZN)、铅(PB)、镍(NI)、锡(SN)、黄金(AU)、白银(AG)

### 黑色金属
螺纹钢(RB)、热卷(HC)、铁矿石(I)、焦炭(J)、焦煤(JM)

### 能源化工
原油(SC)、燃料油(FU)、沥青(BU)、PTA(TA)、甲醇(MA)、塑料(L)、聚丙烯(PP)、乙二醇(EG)

### 农产品
豆粕(M)、豆油(Y)、棕榈油(P)、玉米(C)、白糖(SR)、棉花(CF)、菜粕(RM)、菜油(OI)

### 金融期货
沪深300(IF)、中证500(IC)、上证50(IH)、中证1000(IM)、10年期国债(T)、5年期国债(TF)

---

## 核心指标说明

### 交易指标
| 指标 | 说明 |
|------|------|
| 成交量 | 当日成交手数 |
| 持仓量 | 未平仓合约数量 |
| 换手率 | 成交量/持仓量 |
| 仓差 | 当日持仓量变化 |

### 风险指标
| 指标 | 说明 |
|------|------|
| 波动率 | 收益率标准差(年化) |
| VaR | 风险价值 |
| 最大回撤 | 历史最大亏损 |
| 夏普比率 | 收益风险比 |

### 套利指标
| 指标 | 说明 |
|------|------|
| 价差 | 两合约价格差 |
| 价差均值 | 历史平均价差 |
| Z-Score | (当前-均值)/标准差 |

---

## 使用方法

### 查询市场概览

```bash
cd futures-market-overview
python scripts/main.py --overview
```

### 分析成交持仓

```bash
cd futures-volume-analyzer
python scripts/main.py --symbol RB2501
```

### 计算保证金

```bash
cd futures-margin-calculator
python scripts/main.py --symbol RB2501 --price 3500 --lots 1
```

### 分析套利机会

```bash
cd futures-arbitrage-analyzer
python scripts/main.py --symbol1 RB2501 --symbol2 RB2505
```

### 风险评估

```bash
cd futures-risk-analyzer
python scripts/main.py --symbol RB2501 --lookback 60
```

---

## 文件结构

```
futures-suite/
├── README.md
├── futures-market-overview/
│   ├── SKILL.md
│   ├── LICENSE
│   ├── requirements.txt
│   └── scripts/
│       └── main.py
├── futures-volume-analyzer/
│   └── ...
├── futures-margin-calculator/
│   └── ...
├── futures-arbitrage-analyzer/
│   └── ...
├── futures-risk-analyzer/
│   └── ...
├── commodity-futures-analyzer/
│   └── ...
├── financial-futures-analyzer/
│   └── ...
├── futures-position-tracker/
│   └── ...
├── futures-delivery-analyzer/
│   └── ...
└── futures-macro-correlation/
    └── ...
```

---

## 依赖安装

```bash
# 安装基础依赖
pip install akshare pandas numpy requests
```

---

## 注意事项

1. **真实数据源**：所有Skills均使用真实数据源
2. **API限制**：部分数据源有调用频率限制
3. **数据更新**：行情数据实时更新，历史数据每日更新
4. **保证金率**：保证金率会随市场风险调整，请以交易所最新公告为准

---

## 项目信息

- **开发方**: FinClaw Project
- **许可证**: MIT License
- **创建时间**: 2026-03-22
- **技能数量**: 10个
