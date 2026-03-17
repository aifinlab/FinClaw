---
name: a-share-portfolio-optimize
description: A股量化组合优化。当用户说"组合优化"、"portfolio optimization"、"均值方差"、"风险平价"、"最优权重"、"Black-Litterman"、"最小方差"、"最大夏普"、"怎么分配权重"、"等风险贡献"时触发。基于现代投资组合理论，对给定标的池进行量化权重优化，支持均值方差/最小方差/风险平价/等权等多种方法，输出最优配置权重和有效前沿。支持研报风格（formal）和快速优化风格（brief）。
---

### 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 各资产日K线（用于计算收益率序列和协方差矩阵）
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [起始日期]

# 各资产最新行情
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE1],[CODE2],[CODE3],...

# 无风险利率参照（十年期国债收益率，可手动指定，默认2.5%）
# 大盘基准（有效前沿对比）
python "$SCRIPTS/cn_stock_data.py" kline --code SH000300 --freq daily --start [起始日期]
```

### 量化优化脚本
```bash
OPTIM="$SKILLS_ROOT/a-share-portfolio-optimize/scripts"

# 给定资产收益率矩阵，运行组合优化
python "$OPTIM/portfolio_optimizer.py" \
  --returns_csv [收益率CSV路径] \
  --method [min_var|max_sharpe|risk_parity|equal_weight] \
  --rf 0.025 \
  --long_only \
  --max_weight 0.40
```

### Workflow (5 steps):

**Step 1: 输入资产池与约束**

收集用户信息：
| 项目 | 说明 | 默认值 |
|------|------|--------|
| 资产池 | 股票代码列表 | 用户提供 |
| 历史窗口 | 用于估计参数的历史区间 | 近1年（250交易日） |
| 优化方法 | min_var / max_sharpe / risk_parity / equal_weight / BL | max_sharpe |
| 无风险利率 | Rf | 2.5% |
| 约束条件 | 做多约束、个股上限、行业上限 | long_only, max 40% |
| 预期观点(BL) | 用户主观收益预期（仅BL模型需要） | - |

**Step 2: 数据获取与收益率/风险估计**

1. 通过 cn-stock-data kline 获取各资产日K线
2. 计算日收益率序列 -> 年化收益率向量 mu
3. 计算收益率协方差矩阵 Sigma（默认样本协方差，可选 Ledoit-Wolf 收缩）
4. 展示关键统计：

| 代码 | 名称 | 年化收益(%) | 年化波动(%) | 夏普比 | 最大回撤(%) |
|------|------|-----------|-----------|-------|-----------|

相关系数矩阵热力图描述（哪些资产高度正相关、哪些负相关/低相关提供分散化收益）。

**Step 3: 组合优化求解**

根据用户选择的方法执行优化：

**方法 A: 均值方差 / 最大夏普 (MVO - Max Sharpe)**
- 目标: max (mu^T w - Rf) / sqrt(w^T Sigma w)
- 约束: sum(w)=1, w>=0 (long_only), w_i<=max_weight

**方法 B: 最小方差 (Min Variance)**
- 目标: min w^T Sigma w
- 约束: sum(w)=1, w>=0

**方法 C: 风险平价 (Risk Parity)**
- 目标: 各资产风险贡献相等 RC_i = w_i * (Sigma w)_i / sqrt(w^T Sigma w) = 1/N
- 数值求解: min sum_i (RC_i - 1/N)^2

**方法 D: 等权 (Equal Weight)**
- w_i = 1/N (作为基准参照)

**方法 E: Black-Litterman (可选)**
- 均衡收益 pi = delta * Sigma * w_mkt
- 融合用户观点: mu_BL = [(tau*Sigma)^-1 + P^T Omega^-1 P]^-1 [(tau*Sigma)^-1 pi + P^T Omega^-1 Q]
- 基于 mu_BL 再做 MVO

调用 portfolio_optimizer.py 执行计算，输出最优权重。

**Step 4: 结果展示与有效前沿**

**最优权重**：
| 代码 | 名称 | 权重(%) | 风险贡献(%) |
|------|------|---------|-----------|

**组合预期指标**：
| 指标 | 最优组合 | 等权组合 | 沪深300 |
|------|---------|---------|---------|
| 预期年化收益(%) | | | |
| 预期年化波动(%) | | | |
| 夏普比 | | | |
| 最大回撤(%) | | | |

**有效前沿描述**：
- 最小方差组合位置（收益-波动坐标）
- 最大夏普组合位置（切线组合）
- 各个股在收益-风险平面上的位置
- 当前组合相对有效前沿的位置

**Step 5: 输出**

### 风格说明
| 维度 | formal（量化研报风格） | brief（快速优化风格） |
|------|---------------------|---------------------|
| 篇幅 | 4-6 页 | 1-2 页 |
| 统计分析 | 完整收益/风险/相关性矩阵 | 关键指标摘要 |
| 优化方法 | 多方法对比 + 有效前沿 | 单一方法结果 |
| 权重输出 | 完整表格 + 风险贡献分解 | 权重饼图描述 |
| 敏感性 | 参数敏感性分析 | 不含 |
| 理论说明 | 含模型原理简述 | 不含 |
| 免责声明 | 需要 | 不需要 |

### 关键规则
1. **历史不代表未来**：基于历史数据的优化结果仅供参考，必须声明"过去业绩不预测未来收益"
2. **估计误差**：均值估计不稳定，优先推荐最小方差或风险平价等不依赖收益率估计的方法
3. **协方差稳定性**：短期协方差可能不稳定，建议使用至少1年数据，可选 Ledoit-Wolf 收缩估计
4. **约束合理性**：默认做多约束（A股做空受限），个股上限40%防止过度集中
5. **多方法对比**：formal 风格下建议对比多种方法结果，让用户理解不同优化目标的权衡
6. **与其他 skill 联动**：可用 a-share-comps 补充估值视角、a-share-technical 确认技术面、a-share-sector 检查行业暴露
7. **Black-Litterman 谨慎使用**：BL 模型需要用户提供主观观点，引导用户合理设定观点及置信度
