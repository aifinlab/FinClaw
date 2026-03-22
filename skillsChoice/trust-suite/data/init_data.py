#!/usr/bin/env python3
"""
信托数据初始化与测试脚本
初始化数据库表结构并测试数据对接（含同花顺API）
"""

import sys
import os

# 设置环境变量（如已设置则使用已设置的值）
if not os.getenv('THS_ACCESS_TOKEN'):
    os.environ['THS_ACCESS_TOKEN'] = '1f85469c0d451daee3b7459128105b38f5f488ff.signs_ODQ0NjM0NjEz'

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trust_data_adapter import get_data_provider, TrustDataProvider

def test_data_connection():
    """测试数据连接"""
    print("=" * 60)
    print("信托数据对接层初始化测试")
    print("=" * 60)
    
    provider = get_data_provider()
    
    # 1. 测试数据源状态
    print("\n📊 数据源状态检查")
    print("-" * 40)
    info = provider.get_data_source_info()
    available_count = 0
    for adapter in info['adapters']:
        status = "✅ 可用" if adapter['available'] else "❌ 不可用"
        print(f"  {adapter['name']}: {status}")
        if adapter['available']:
            available_count += 1
    
    print(f"\n可用数据源: {available_count}/{len(info['adapters'])}")
    
    # 2. 测试同花顺API
    print("\n📈 同花顺API测试")
    print("-" * 40)
    
    # 测试信托公司财务数据
    print("  1) 获取信托公司财务数据...")
    financials = provider.get_trust_company_financials('平安信托')
    if financials:
        print(f"     ✅ {financials['company']}")
        print(f"        ROE: {financials.get('roe')}%")
        print(f"        净利润: {financials.get('net_profit')}亿元")
        print(f"        营收增长率: {financials.get('revenue_growth')}%")
    else:
        print("     ❌ 未获取到数据")
    
    # 测试行业指数
    print("  2) 获取信托行业指数...")
    index_data = provider.get_trust_industry_index()
    if index_data:
        print(f"     ✅ {index_data['index_name']}")
        print(f"        当前点位: {index_data.get('current_price')}")
        print(f"        涨跌幅: {index_data.get('change')}%")
    else:
        print("     ❌ 未获取到数据")
    
    # 测试头部公司
    print("  3) 获取头部信托公司行情...")
    companies = provider.get_top_trust_companies()
    if companies:
        print(f"     ✅ 获取到 {len(companies)} 家公司")
        for c in companies[:3]:
            change = c.get('change_pct', 0)
            emoji = "📈" if change and change > 0 else "📉" if change and change < 0 else "➡️"
            print(f"        {emoji} {c['company']}: {change}%")
    else:
        print("     ❌ 未获取到数据")
    
    # 3. 测试产品数据获取
    print("\n📦 产品数据测试")
    print("-" * 40)
    
    test_cases = [
        {'desc': '全部产品', 'filters': {}},
        {'desc': '高收益产品(≥7.5%)', 'filters': {'min_yield': 7.5}},
        {'desc': '短期产品(≤18月)', 'filters': {'max_duration': 18}},
        {'desc': 'R2风险产品', 'filters': {'risk_level': ['R2']}},
    ]
    
    for case in test_cases:
        products = provider.get_products(**case['filters'])
        print(f"  {case['desc']}: {len(products)}个产品")
        for p in products[:2]:
            print(f"    - {p.product_name[:20]}... {p.expected_yield}%/{p.duration}月/{p.risk_level}")
    
    # 4. 测试市场统计
    print("\n📈 市场统计数据")
    print("-" * 40)
    stats = provider.get_market_stats()
    if stats:
        print(f"  统计日期: {stats.stat_date}")
        print(f"  发行规模: {stats.total_issuance}亿元")
        print(f"  产品数量: {stats.product_count}个")
        print(f"  平均收益: {stats.avg_yield}%")
        
        print(f"\n  分类型收益率:")
        for type_name, yield_val in stats.yield_by_type.items():
            print(f"    {type_name}: {yield_val}%")
        
        print(f"\n  分期限收益率:")
        for duration, yield_val in stats.yield_by_duration.items():
            print(f"    {duration}: {yield_val}%")
    else:
        print("  无法获取市场统计数据")
    
    # 5. 测试收益率曲线
    print("\n📉 收益率曲线")
    print("-" * 40)
    curve = provider.get_yield_curve()
    if not curve.empty:
        print(curve.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("数据对接层初始化完成")
    print("=" * 60)

if __name__ == '__main__':
    test_data_connection()
