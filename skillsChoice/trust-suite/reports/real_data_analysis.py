#!/usr/bin/env python3
"""
信托产品分析 - 使用真实数据源(同花顺API)
"""

import sys
import os
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/trust-suite/data')

# 设置Token
os.environ['THS_ACCESS_TOKEN'] = 'b06d60d5efce5454b45a29cde92a1e892019ca45.signs_ODQ0NjM0NjEz'

from ths_adapter import ThsTrustDataAdapter
from datetime import datetime

def analyze_trust_products():
    print('=' * 70)
    print('🏦 信托产品分析报告 (真实数据源)')
    print('=' * 70)
    print(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'数据来源: 同花顺iFinD API')
    print()
    
    # 初始化适配器
    adapter = ThsTrustDataAdapter(os.getenv('THS_ACCESS_TOKEN'))
    
    # 检查API可用性
    if not adapter.is_available():
        print('❌ 同花顺API不可用')
        return
    
    print('✅ 同花顺API连接成功')
    print()
    
    # 获取头部信托公司行情
    print('-' * 70)
    print('📊 一、头部信托公司行情')
    print('-' * 70)
    
    companies = adapter.get_top_trust_companies()
    print(f'获取到 {len(companies)} 家信托公司:\n')
    
    # 按涨跌幅排序
    sorted_companies = sorted(companies, 
                              key=lambda x: x.get('change', 0) or 0, 
                              reverse=True)
    
    for i, c in enumerate(sorted_companies, 1):
        change = c.get('change', 0) or 0
        price = c.get('price')
        
        if price is None:
            status = '➖ 停牌/无数据'
        elif change > 0:
            status = f'📈 +{change:.2f}'
        elif change < 0:
            status = f'📉 {change:.2f}'
        else:
            status = '➡️ 0.00'
        
        price_str = f'¥{price:.2f}' if price else '¥--'
        print(f"{i:2d}. {c['company']:10s} {price_str:10s} {status}")
    
    # 分析统计
    valid_prices = [c.get('price') for c in companies if c.get('price')]
    valid_changes = [c.get('change', 0) for c in companies if c.get('price')]
    
    if valid_changes:
        avg_change = sum(valid_changes) / len(valid_changes)
        up_count = sum(1 for x in valid_changes if x > 0)
        down_count = sum(1 for x in valid_changes if x < 0)
        
        print()
        print('市场统计:')
        print(f'   平均涨跌: {avg_change:+.2f}')
        print(f'   上涨家数: {up_count}家')
        print(f'   下跌家数: {down_count}家')
    
    # 财务数据分析
    print()
    print('-' * 70)
    print('💰 二、重点公司财务分析')
    print('-' * 70)
    
    target_companies = ['平安信托', '中航信托', '五矿信托']
    
    for company in target_companies:
        print(f'\n【{company}】')
        try:
            financials = adapter.get_trust_company_financials(company)
            
            if financials:
                print(f'   股票代码: {financials.get("stock_code", "N/A")}')
                print(f'   ROE: {financials.get("roe", "N/A")}')
                print(f'   净利润: {financials.get("net_profit", "N/A")}')
                print(f'   营收: {financials.get("revenue", "N/A")}')
            else:
                print('   ⚠️  财务数据获取失败(需确认指标代码)')
        except Exception as e:
            print(f'   ⚠️  财务数据获取失败: {str(e)[:50]}')
    
    # 总结
    print()
    print('=' * 70)
    print('📋 三、分析总结')
    print('=' * 70)
    print(f'数据来源: 同花顺iFinD API')
    print(f'数据类型: 实时行情')
    print(f'覆盖公司: {len(companies)}家头部信托公司')
    print()
    print('数据说明:')
    print('  • 股价数据: 实时行情(同花顺API)')
    print('  • 涨跌幅: 当日涨跌')
    print('  • 财务数据: 部分指标需确认代码后获取')
    print()
    print('=' * 70)

if __name__ == '__main__':
    analyze_trust_products()
