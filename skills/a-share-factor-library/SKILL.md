---
name: a-share-factor-library
description: A股量化因子库/因子速查/因子计算公式查询。当用户说"因子库"、"有哪些因子"、"factor library"、"怎么算XX因子"、"价值因子"、"动量因子"、"质量因子"、"波动率因子"、"因子定义"、"因子公式"、"查因子"、"因子速查"、"列出所有因子"、"EP怎么算"、"BP公式"、"因子字段"时触发。MUST USE when user asks for factor definitions, formulas, or wants to look up how a specific quantitative factor is calculated. 提供A股常用量化因子的完整定义、计算公式、数据字段映射，覆盖价值/成长/质量/动量/波动率/规模/流动性七大类50+因子。支持研报风格（formal）和快速查询风格（brief）。
---

# A股常用因子库速查 (a-share-factor-library)

## 核心能力
- **因子目录**: 7大类 50+ 因子的完整定义、公式、数据字段映射
- **因子计算**: 给定股票代码，实际计算因子值（调用 cn-stock-data）
- **因子速查**: 按类别/名称/英文缩写快速定位因子
- **因子对比**: 同类因子横向比较，解释差异与适用场景

## 数据来源
- **财务因子**: `cn-stock-data finance`（adata 43字段: basic_eps, roe_wtd, roa_wtd, gross_margin, net_margin, total_rev, net_profit_attr_sh, total_rev_yoy_gr, net_profit_yoy_gr 等）
- **行情因子**: `cn-stock-data kline`（date, open, close, high, low, volume, amount, turnover_rate, pct_change）
- **实时数据**: `cn-stock-data quote`（price, pe_ttm, market_cap, float_market_cap, volume_ratio）

## CLI 用法
```bash
SCRIPTS_DIR="$SKILLS_ROOT/a-share-factor-library/scripts"
CN_STOCK="$SKILLS_ROOT/cn-stock-data/scripts"

# 计算单个因子
python "$SCRIPTS_DIR/factor_calculator.py" --factor ep --codes SH600519,SZ000858

# 动量因子
python "$SCRIPTS_DIR/factor_calculator.py" --factor momentum_6m --codes SH600519

# 批量计算一类因子
python "$SCRIPTS_DIR/factor_calculator.py" --category value --codes SH600519,SZ000858

# 列出所有因子
python "$SCRIPTS_DIR/factor_calculator.py" --list

# 查看某个因子定义
python "$SCRIPTS_DIR/factor_calculator.py" --info ep
```

## 因子参考目录
详见 `references/factor-library-catalog.md`，包含全部 7 大类因子的：
- 中英文名称
- 计算公式
- cn-stock-data 字段映射
- 因子方向（正/负）
- 适用行业说明

## Workflow (5 steps)

### Step 1: 识别因子类别
根据用户请求判断：
- 具体因子查询 → 定位到 catalog 中的因子卡片
- 因子类别浏览 → 列出该类别全部因子
- 因子计算 → 进入 Step 3-4
- 因子对比 → 列出多个因子的公式与差异

### Step 2: 查找因子定义与公式
从 `references/factor-library-catalog.md` 查找：
- 因子名称（中/英）
- 计算公式（数学表达式）
- 所需数据字段
- 因子方向与适用说明

### Step 3: 映射到 cn-stock-data 字段
将因子公式中的变量映射到实际数据接口：
- 财务类 → `cn-stock-data finance --code XXX`
- 行情类 → `cn-stock-data kline --code XXX --freq daily --start YYYY-MM-DD`
- 估值类 → `cn-stock-data quote --code XXX`

### Step 4: 计算因子值
调用 `scripts/factor_calculator.py` 或手动计算：
```bash
python "$SCRIPTS_DIR/factor_calculator.py" --factor <factor_name> --codes <code1,code2,...>
```

### Step 5: 输出因子卡片

**formal（研报风格）**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
因子名称: EP（盈利收益率）
英文全称: Earnings-to-Price Ratio
类别: 价值因子 | 方向: 正向（越大越便宜）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
公式: EP = EPS_TTM / Price = 1 / PE_TTM
数据源: cn-stock-data quote → pe_ttm
适用行业: 全行业（金融/周期股慎用）

计算结果:
| 股票 | EPS_TTM | Price | EP | 排名 |
|------|---------|-------|----|------|
| 贵州茅台 | 66.3 | 1895.5 | 0.035 | 1 |
| 五粮液 | 7.2 | 168.0 | 0.043 | 2 |

因子解读:
EP 值越大说明股票越"便宜"，是经典价值因子。
建议与 BP、CFP 等因子组合使用，避免单一因子陷阱。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**brief（快速查询风格）**:
```
EP = 1/PE_TTM | 方向:正 | 数据:quote.pe_ttm
SH600519: EP=0.035 | SZ000858: EP=0.043
```

## 注意事项
- 财务因子使用最近一期报告期数据，注意时效性
- 动量/波动率因子需要足够长度的历史 K 线（至少 1 年）
- 行业中性化处理不在本 skill 范围内，如需请参考 a-share-stock-screen
- 因子方向说明：正向=值越大越好（如 ROE），负向=值越小越好（如 PE）
