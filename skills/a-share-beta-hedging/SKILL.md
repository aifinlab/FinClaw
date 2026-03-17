---
name: a-share-beta-hedging
description: A股Beta对冲/市场中性策略。当用户说"对冲"、"beta hedging"、"市场中性"、"对冲策略"、"怎么对冲"、"空头对冲"时触发。量化构建市场中性组合。支持formal和brief风格。
---

# A股Beta对冲/市场中性策略

## 数据源
```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"
python "$SCRIPTS/cn_stock_data.py" kline --code [CODE] --freq daily --start [日期]
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]
```

## Workflow
### Step 1: 计算个股/组合Beta
- 回归法：R_i = α + β × R_m + ε（60日滚动）
- 调整Beta = 0.67 × Raw Beta + 0.33 × 1
### Step 2: 对冲工具选择
- 股指期货（IF/IC/IM/IH）
- ETF融券（如300ETF、500ETF）
- 期权组合
### Step 3: 计算对冲比率
- 全对冲：空头名义值 = 多头名义值 × β
- 部分对冲：根据风险预算调整对冲比例
### Step 4: 基差风险分析
- 期货贴水/升水对对冲成本的影响
- 展期成本估算
### Step 5: 输出
| 维度 | formal | brief |
|------|--------|-------|
| Beta计算 | 多种方法对比 | 当前Beta |
| 对冲方案 | 完整对冲方案 | 推荐工具+比率 |
| 成本分析 | 基差+展期成本 | 年化对冲成本 |
默认风格：brief。

## 关键规则
1. Beta不稳定——需用滚动窗口动态调整
2. A股股指期货长期贴水——对冲成本=贴水+手续费
3. 融券难借且成本高——限制了做空能力
4. 对冲只消除Beta风险——Alpha也可能为负
5. 对冲比例非一成不变——需定期再平衡
