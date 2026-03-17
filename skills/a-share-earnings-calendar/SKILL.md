---
name: a-share-earnings-calendar
description: A股财报日历/业绩预告汇总。当用户说"财报日历"、"业绩预告"、"什么时候发财报"、"XX什么时候出报告"、"earnings calendar"、"最近谁发财报"、"业绩快报"、"业绩预告汇总"、"哪些公司业绩超预期"时触发。汇总近期已发布和即将发布的财报/业绩预告，分析业绩超预期和不及预期的情况。支持研报风格（formal）和快速查询风格（brief）。不适用于个股深度财报分析（用 a-share-earnings-analysis）。
---

# A股财报日历/业绩预告汇总

## 数据源

```bash
SCRIPTS="$SKILLS_ROOT/cn-stock-data/scripts"

# 个股财务数据（已发布的）
python "$SCRIPTS/cn_stock_data.py" finance --code [CODE]

# 个股行情（看业绩公告后股价反应）
python "$SCRIPTS/cn_stock_data.py" quote --code [CODE]
```

核心数据通过 akshare 获取：
```bash
# 业绩预告汇总（date 格式 YYYYMMDD，取季末日期：0331/0630/0930/1231）
python -c "import akshare as ak; df=ak.stock_yjyg_em(date='20260331'); print(df.head(20).to_json(orient='records', force_ascii=False))"

# 业绩快报
python -c "import akshare as ak; df=ak.stock_yjkb_em(date='20260331'); print(df.head(20).to_json(orient='records', force_ascii=False))"
```

补充：用 web 搜索获取财报披露时间表、市场一致预期、分析师预测。

## Workflow

1. **确定查询范围** — 即将发布财报的公司 / 已发布业绩预告汇总 / 特定公司财报时间
2. **数据获取** — 根据当前日期推断对应报告期（date 参数），拉取业绩预告/快报数据；必要时 web 搜索披露排期
3. **业绩梳理**
   - 按类型分类汇总：预增/预减/扭亏/首亏/续盈/续亏/略增/略减
   - 超预期/不及预期筛选（vs 市场一致预期 or 前期预告中值）
   - 按行业分组统计，找出景气行业和承压行业
4. **市场反应分析** — 已公布业绩的公司，拉取公告后股价表现（1日/3日/5日涨跌幅）
5. **输出** — 根据风格生成报告

## 风格

| 维度 | formal | brief |
|------|--------|-------|
| 输出 | 完整业绩日历报告 | 关键信息列表 |
| 覆盖 | 全市场统计+重点个股 | 仅用户关注的个股/板块 |
| 分析 | 超预期/低于预期详细分析 | 预增/预减数量统计 |
| 时间表 | 未来2周完整披露排期 | 近期重点关注 |

默认 brief；用户要求"详细/报告/研报"时用 formal。

## 关键规则

1. **披露截止日**：年报/一季报 4月30日前，中报 8月31日前，三季报 10月31日前
2. **数据可靠性**：正式财报 > 业绩快报 > 业绩预告（预告通常给范围）
3. **"超预期"需有参照**：市场一致预期 or 前期预告范围中值 or 历史增速趋势
4. **区分"已发布"和"即将发布"**，所有数据标注时效
5. **date 参数映射**：根据当前日期推断最近报告期季末日（0331/0630/0930/1231）
6. 参考 `references/earnings-calendar-guide.md` 了解业绩预告类型定义和财报季节奏
