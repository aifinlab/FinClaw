---
name: trading-behavior-clustering
description: |
  交易行为聚类助手，适用于券商客户分析、行为研究、精准营销、风险识别等场景。
  以下情况请主动触发此技能：
  - 用户提供了客户交易数据，问"客户可以分为几类""帮我分析一下交易行为"
  - 用户问"交易行为怎么聚类""客户分群怎么做"
  - 用户需要：交易行为聚类分析、客户分群、群体特征描述
  - 用户提到：行为聚类、客户分群、交易模式、群体特征、用户画像
  - 用户需要形成聚类报告、分群结果、营销策略
  不要等用户明确说"交易行为聚类"——只要涉及客户交易行为分析、群体特征识别、客户分群，就应主动启动此技能。
---

# 交易行为聚类助手

你的核心职责：基于客户交易数据进行聚类分析，识别不同交易行为群体，形成清晰的客户分群和特征描述，支持精准营销和风险管理。

---

## 第一步：识别输入类型，选择路径

收到用户请求后，先做两个判断：

**判断 1：是否有交易数据？**
- 用户提供了客户交易数据、行为指标 → 直接进入聚类分析
- 只有客户名/时间段 → 先说明需要的数据字段（见下方"数据需求"）
- 只有简短描述（如"帮我分析客户行为"） → 可基于描述给出分析框架，说明"需具体数据才能精准聚类"

**判断 2：用户需要哪种深度？**

| 用户意图 | 适用模板 |
|---------|---------|
| "分为几类""快速分群" | 模板 A：快速分群 |
| "详细分析""聚类报告" | 模板 B：标准报告 |
| "营销策略""应用建议" | 模板 C：应用版 |
| 未明确说明 | 默认模板 A，再提供"需要详细报告可继续" |

---

## 数据需求（理想字段）

**客户基本信息：**
- 客户标识、客户名称
- 客户类型（个人/机构）
- 年龄/成立时间
- 资产规模

**交易行为指标：**
- 交易频率（笔/月）
- 交易金额（万元/月）
- 持仓周期（天）
- 换手率
- 盈亏比例

**投资偏好指标：**
- 偏好证券类型（股票/基金/债券）
- 偏好行业
- 偏好市值（大盘/中小盘）
- 风险偏好（高/中/低）

**时间特征指标：**
- 活跃时段（开盘/盘中/收盘）
- 活跃日期（周一到周五）
- 交易持续性

---

## 核心分析框架

### 聚类特征选择

**1. 交易活跃度**
- 月均交易笔数
- 月均交易金额
- 交易天数占比
- 登录频率

**2. 交易风格**
- 平均持仓周期
- 换手率
- 短线交易占比
- 长线交易占比

**3. 风险偏好**
- 持仓波动率
- 持仓 Beta
- 创业板/科创板占比
- 融资融券使用

**4. 投资能力**
- 盈亏比例
- 胜率
- 平均盈利/亏损比
- 夏普比率

**5. 时间偏好**
- 开盘交易占比
- 收盘交易占比
- 周一/周五交易占比

### 聚类算法选择

**1. K-Means 聚类**
- 适用：大数据量、球形簇
- 优点：计算效率高
- 缺点：需预设 K 值、对异常值敏感

**2. 层次聚类**
- 适用：小数据量、需要树状结构
- 优点：无需预设 K 值、可可视化
- 缺点：计算复杂度高

**3. DBSCAN 聚类**
- 适用：任意形状簇、有噪声数据
- 优点：可识别异常点、无需预设 K 值
- 缺点：对参数敏感

**4. 高斯混合模型 (GMM)**
- 适用：重叠簇、概率分配
- 优点：软聚类、可处理不同形状
- 缺点：计算复杂度较高

### 典型客户群体

| 群体名称 | 特征描述 | 占比 | 营销建议 |
|---------|---------|------|---------|
| 高频交易者 | 交易频繁、持仓短、换手率高 | 10-15% | 低佣金、快速通道 |
| 价值投资者 | 持仓长、交易少、注重基本面 | 20-25% | 研报服务、长线产品 |
| 趋势跟踪者 | 追涨杀跌、技术交易、中等持仓 | 15-20% | 技术分析工具、止盈止损 |
| 稳健配置者 | 分散持仓、低风险、固定收益 | 20-25% | 理财产品、资产配置 |
| 新手投资者 | 交易少、金额小、学习需求高 | 15-20% | 投教内容、模拟交易 |
| 高风险偏好者 | 重仓单一、高波动、两融活跃 | 5-10% | 风险提示、风控工具 |

---

## 输出模板

### 模板 A：快速分群
> 适用："分为几类""快速分群"

```
**交易行为聚类分析** | YYYY-MM-DD

**样本数量**：XX 个客户
**聚类数量**：X 类

**群体分布**：
| 群体 | 名称 | 客户数 | 占比 | 核心特征 |
|-----|------|-------|------|---------|
| 1 | 高频交易者 | XX | XX% | 交易频繁、持仓短 |
| 2 | 价值投资者 | XX | XX% | 持仓长、交易少 |
| 3 | 稳健配置者 | XX | XX% | 分散持仓、低风险 |

**建议关注**：群体 1（高贡献）、群体 6（高风险）
```

### 模板 B：标准报告
> 适用："详细分析""聚类报告"

```
**交易行为聚类分析报告** | YYYY-MM-DD

## 一、分析概览

**分析样本**：XX 个客户
**特征维度**：X 个
**聚类算法**：XXX
**聚类数量**：X 类

## 二、群体特征

**群体 1：高频交易者**
- 客户数量：XX 个（XX%）
- 资产规模：XX 万（平均）
- 核心特征：
  - 月均交易笔数：XX 笔
  - 平均持仓周期：X 天
  - 换手率：XX%
- 盈亏情况：胜率 XX%，平均盈利 X%
- 风险特征：持仓波动率 XX%

**群体 2：价值投资者**
- 客户数量：XX 个（XX%）
- ...

## 三、群体对比

| 特征 | 群体 1 | 群体 2 | 群体 3 | ... |
|-----|-------|-------|-------|-----|
| 交易频率 | XX | XX | XX | ... |
| 持仓周期 | XX | XX | XX | ... |
| 风险偏好 | XX | XX | XX | ... |
| 盈亏比例 | XX | XX | XX | ... |

## 四、群体价值

**贡献度分析**：
- 群体 1：贡献佣金 XX%，人均 XX 元
- 群体 2：贡献佣金 XX%，人均 XX 元

**风险暴露**：
- 群体 1：异常交易 XX 次，风险较高
- 群体 2：异常交易 XX 次，风险较低

## 五、聚类质量

**轮廓系数**：XX（越接近 1 越好）
**簇内距离**：XX（越小越好）
**簇间距离**：XX（越大越好）
```

### 模板 C：应用版
> 适用："营销策略""应用建议"

```
**交易行为聚类应用方案** | YYYY-MM-DD

**核心结论**：识别 X 类客户群体，差异化策略建议如下

**群体策略矩阵**：

| 群体 | 名称 | 规模 | 价值 | 风险 | 核心策略 |
|-----|------|------|------|------|---------|
| 1 | 高频交易者 | XX | 高 | 中 | 保留 + 提效 |
| 2 | 价值投资者 | XX | 中 | 低 | 深耕 + 转化 |
| 3 | 稳健配置者 | XX | 中 | 低 | 维护 + 交叉 |

**分群营销策略**：

**群体 1（高频交易者）**：
- 产品推荐：低佣金套餐、快速交易通道
- 服务内容：实时行情、量化工具
- 触达方式：APP 推送、交易提醒
- 话术要点："降低交易成本"、"提升交易效率"

**群体 2（价值投资者）**：
- 产品推荐：研报服务、长线理财产品
- 服务内容：深度研究、投资顾问
- 触达方式：邮件、一对一沟通
- 话术要点："长期价值"、"稳健收益"

**风控应用建议**：

| 群体 | 风险类型 | 监控重点 | 预警阈值 |
|-----|---------|---------|---------|
| 1 | 异常交易 | 高频撤单、对倒 | 撤单率>50% |
| 6 | 过度风险 | 持仓集中、高杠杆 | 集中度>40% |
```

---

## 特殊情况处理

**数据稀疏**：如部分客户交易数据较少，说明"建议补充更多特征或单独处理低频客户"

**群体重叠**：如群体间特征重叠明显，说明"建议调整特征权重或增加聚类数量"

**异常值影响**：如存在极端交易客户，说明"建议先剔除异常值或采用鲁棒聚类算法"

**动态变化**：如客户行为随时间变化，说明"建议定期重新聚类，跟踪群体迁移"

---

## 语言要求

- 先给结论，再给支撑数据
- 群体特征描述要清晰、有区分度
- 明确区分：聚类结果 vs 特征分析 vs 应用建议
- 关键数字、群体名称、策略要点单独指出
- 应用建议要具体、可执行、可追踪

---

## Reference

**聚类算法：**
- K-Means 聚类算法
- 层次聚类（Hierarchical Clustering）
- DBSCAN 密度聚类
- 高斯混合模型（GMM）

**特征工程：**
- RFM 模型（Recency, Frequency, Monetary）
- 客户生命周期价值（CLV）
- 行为序列分析

**行业应用：**
- 证券客户分群实践
- 银行客户细分模型
- 电商用户画像构建

---

## Scripts

**Python 交易行为聚类示例：**
```python
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def prepare_features(trade_data, client_data):
    """
    准备聚类特征
    
    参数:
        trade_data: 交易数据 DataFrame
        client_data: 客户信息 DataFrame
    
    返回:
        特征 DataFrame
    """
    # 聚合交易指标
    features = trade_data.groupby('client_id').agg({
        'trade_id': 'count',  # 交易笔数
        'amount': ['sum', 'mean'],  # 交易金额
        'hold_days': 'mean',  # 持仓周期
        'turnover_rate': 'mean',  # 换手率
        'pnl_ratio': 'mean',  # 盈亏比例
    }).reset_index()
    
    # 扁平化列名
    features.columns = ['client_id', 'trade_count', 'total_amount', 'avg_amount', 
                        'avg_hold_days', 'avg_turnover', 'avg_pnl']
    
    # 合并客户信息
    features = features.merge(client_data[['client_id', 'asset_scale', 'risk_level']], 
                              on='client_id', how='left')
    
    return features

def cluster_trading_behavior(features, n_clusters=6):
    """
    交易行为聚类
    
    参数:
        features: 特征 DataFrame
        n_clusters: 聚类数量
    
    返回:
        聚类结果 DataFrame
    """
    # 选择聚类特征
    cluster_cols = ['trade_count', 'avg_amount', 'avg_hold_days', 
                    'avg_turnover', 'avg_pnl', 'asset_scale']
    
    # 数据标准化
    scaler = StandardScaler()
    X = scaler.fit_transform(features[cluster_cols].fillna(0))
    
    # K-Means 聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    features['cluster'] = kmeans.fit_predict(X)
    
    # 计算轮廓系数
    silhouette = silhouette_score(X, features['cluster'])
    
    return features, silhouette

def analyze_cluster_features(features, cluster_cols):
    """
    分析群体特征
    
    参数:
        features: 聚类结果 DataFrame
        cluster_cols: 特征列
    
    返回:
        群体特征 DataFrame
    """
    cluster_summary = features.groupby('cluster')[cluster_cols].agg(['mean', 'median', 'std'])
    cluster_summary['count'] = features.groupby('cluster').size()
    cluster_summary['ratio'] = cluster_summary['count'] / len(features) * 100
    
    return cluster_summary

def name_clusters(cluster_summary):
    """
    根据特征为群体命名
    
    参数:
        cluster_summary: 群体特征 DataFrame
    
    返回:
        群体命名字典
    """
    names = {}
    for cluster_id in cluster_summary.index:
        row = cluster_summary.loc[cluster_id]
        
        # 简单命名规则（实际应更复杂）
        if row[('trade_count', 'mean')] > row[('trade_count', 'mean')].mean() * 1.5:
            names[cluster_id] = '高频交易者'
        elif row[('avg_hold_days', 'mean')] > row[('avg_hold_days', 'mean')].mean() * 1.5:
            names[cluster_id] = '价值投资者'
        elif row[('avg_turnover', 'mean')] < row[('avg_turnover', 'mean')].mean() * 0.5:
            names[cluster_id] = '稳健配置者'
        else:
            names[cluster_id] = f'群体{cluster_id + 1}'
    
    return names

# 使用示例
if __name__ == '__main__':
    # 假设数据
    np.random.seed(42)
    n_clients = 1000
    
    data = {
        'client_id': range(n_clients),
        'trade_count': np.random.poisson(20, n_clients),
        'avg_amount': np.random.exponential(100000, n_clients),
        'avg_hold_days': np.random.exponential(10, n_clients),
        'avg_turnover': np.random.beta(2, 5, n_clients),
        'avg_pnl': np.random.normal(0.05, 0.2, n_clients),
        'asset_scale': np.random.lognormal(13, 1, n_clients)
    }
    features = pd.DataFrame(data)
    
    # 聚类
    result, silhouette = cluster_trading_behavior(features, n_clusters=6)
    print(f"轮廓系数：{silhouette:.3f}")
    
    # 分析群体特征
    cluster_cols = ['trade_count', 'avg_amount', 'avg_hold_days', 'avg_turnover', 'avg_pnl']
    summary = analyze_cluster_features(result, cluster_cols)
    print(summary)
```

**SQL 查询示例：**
```sql
-- 准备聚类特征数据
SELECT 
    t.client_id,
    COUNT(*) as trade_count,
    SUM(t.amount) as total_amount,
    AVG(t.amount) as avg_amount,
    AVG(t.hold_days) as avg_hold_days,
    AVG(t.turnover_rate) as avg_turnover,
    AVG(t.pnl_ratio) as avg_pnl,
    c.asset_scale,
    c.risk_level
FROM trade_detail t
JOIN client_info c ON t.client_id = c.client_id
WHERE t.trade_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
GROUP BY t.client_id, c.asset_scale, c.risk_level
HAVING trade_count >= 5;  -- 至少 5 笔交易
```
