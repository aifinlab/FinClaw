---
name: insurance-sector-comparison
description: 保险行业对比分析工具。对比国内外保险市场、中外保险公司、不同险种发展。接入AkShare开源保险行业数据，支持实时数据获取和自动更新。适用于国际化研究、竞争分析。
---

# 保险行业对比分析器

## 功能

- 中外保险市场对比（接入AkShare实时数据）
- 保险深度/密度对比
- 国内外保险公司对比
- 不同市场发展阶段
- 中国保险市场结构分析
- 国际经验借鉴
- 自动更新机制

## 数据源

| 数据源 | 接口 | 说明 |
|--------|------|------|
| AkShare | `macro_china_insurance` | 中国保险业经营情况（国家统计局） |
| AkShare | `macro_china_insurance_income` | 原保险保费收入（东方财富） |
| AkShare | `macro_china_gdp` | 中国GDP数据（计算保险深度） |
| 瑞士再保险Sigma报告 | 参考数据 | 全球保险市场参考 |

## 使用方法

```bash
# 全球市场对比（默认）
python scripts/main.py

# 保险深度/密度对比
python scripts/main.py --penetration

# 中国保险市场结构
python scripts/main.py --structure

# 强制更新缓存
python scripts/main.py --force

# 执行自动更新
python scripts/main.py --update
```

## 核心指标

| 指标 | 说明 |
|------|------|
| 保险深度 | 保费/GDP |
| 保险密度 | 人均保费 |
| 渗透率 | 保险普及程度 |
| 赔付率 | 赔付支出/保费收入 |

## 实时数据内容

通过AkShare接口获取的中国保险数据：

- 原保险保费收入
- 财产险保费收入
- 人身险保费收入（寿险、健康险、意外险）
- 原保险赔付支出
- 资产总额
- 业务及管理费
- 银行存款和投资情况

## 自动更新机制

- 缓存有效期：12小时
- 数据源：AkShare开源数据接口
- 失败回退：使用参考数据
- 缓存位置：`data/sector_cache.json`
- 依赖库：`akshare`（需安装）

## 安装依赖

```bash
pip install akshare pandas
```

## 数据说明

- **中国保险数据**：通过AkShare实时获取国家统计局和银保监会公开数据
- **全球市场数据**：参考瑞士再保险Sigma年度报告
- **数据更新频率**：每日（AkShare数据通常有1-2个月滞后）
- **数据质量**：自动检测数据获取状态，失败时提供友好的错误提示

## 计算指标

自动计算的指标包括：
- 保险深度（保费/GDP）
- 简单赔付率
- 财产险/人身险占比
- 人身险内部结构（寿险/健康险/意外险占比）
