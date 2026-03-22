#!/usr/bin/env python3
"""
Fund Suite 数据适配器快速测试
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import akshare as ak

print("=" * 60)
print("Fund Suite 数据适配器测试")
print("=" * 60)

# 测试1: 基金列表
print("\n📍 测试1: 获取基金列表")
try:
    df = ak.fund_name_em()
    print(f"✅ 成功获取 {len(df)} 只基金信息")
    print(f"列名: {df.columns.tolist()}")
    print("\n前5只基金:")
    for _, row in df.head(5).iterrows():
        print(f"  {row['基金代码']} - {row['基金简称']} ({row['基金类型']})")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试2: 搜索基金
print("\n📍 测试2: 搜索基金 '易方达'")
try:
    df = ak.fund_name_em()
    matched = df[df['基金简称'].str.contains('易方达', na=False)]
    print(f"✅ 找到 {len(matched)} 只基金")
    for _, row in matched.head(5).iterrows():
        print(f"  {row['基金代码']} - {row['基金简称']}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试3: 获取基金净值
print("\n📍 测试3: 获取基金净值 (000001 华夏成长)")
try:
    df = ak.fund_open_fund_info_em(symbol="000001")
    print(f"✅ 成功获取 {len(df)} 条净值记录")
    print(f"列名: {df.columns.tolist()}")
    print("\n最近5天净值:")
    for _, row in df.head(5).iterrows():
        print(f"  {row['净值日期']}: 单位净值={row['单位净值']}, 累计净值={row['累计净值']}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试4: 基金排行
print("\n📍 测试4: 获取基金排行")
try:
    df = ak.fund_em_open_fund_rank()
    print(f"✅ 成功获取 {len(df)} 只基金排行")
    print(f"列名: {df.columns.tolist()}")
    print("\n前5只基金收益:")
    for _, row in df.head(5).iterrows():
        print(f"  {row['基金代码']} - {row['基金简称']}: 近1年={row.get('近1年', 'N/A')}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
