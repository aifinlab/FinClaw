#!/usr/bin/env python3
"""
Fund Suite 真实数据使用示例
演示如何使用AkShare/同花顺iFinD获取真实基金数据
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

from fund_data_adapter import get_fund_adapter, FundDataAdapter


def demo_real_data():
    print("=" * 80)
    print("📊 Fund Suite 真实数据源使用示例")
    print("=" * 80)
    
    # 初始化数据适配器
    # 如果不配置同花顺token，会自动使用AkShare
    adapter = get_fund_adapter(prefer_ths=False)
    print(f"\n✅ 当前数据源: {adapter.get_data_source()}")
    
    # ========== 示例1: 搜索基金 ==========
    print("\n" + "-" * 80)
    print("📍 示例1: 搜索基金 '易方达蓝筹'")
    print("-" * 80)
    
    funds = adapter.search_funds("易方达蓝筹")
    print(f"找到 {len(funds)} 只基金:")
    for i, fund in enumerate(funds[:5], 1):
        print(f"  {i}. {fund.fund_code} - {fund.fund_name} ({fund.fund_type})")
    
    if not funds:
        print("  ⚠️ 未找到基金，尝试搜索其他关键词...")
        funds = adapter.search_funds("华夏")
        print(f"\n搜索 '华夏' 找到 {len(funds)} 只基金:")
        for i, fund in enumerate(funds[:5], 1):
            print(f"  {i}. {fund.fund_code} - {fund.fund_name}")
    
    # ========== 示例2: 获取基金净值 ==========
    print("\n" + "-" * 80)
    print("📍 示例2: 获取基金净值历史")
    print("-" * 80)
    
    if funds:
        test_code = funds[0].fund_code
        test_name = funds[0].fund_name
        
        print(f"\n基金: {test_code} ({test_name})")
        print("最近10天净值:")
        
        navs = adapter.get_fund_nav(test_code, days=10)
        if navs:
            print(f"{'日期':<12} {'单位净值':<12} {'日涨跌':<10}")
            print("-" * 40)
            for nav in navs:
                emoji = "📈" if nav.daily_return > 0 else "📉" if nav.daily_return < 0 else "➡️"
                print(f"{nav.date:<12} {nav.nav:<12.4f} {nav.daily_return*100:>+6.2f}% {emoji}")
        else:
            print("  ⚠️ 未能获取净值数据")
    
    # ========== 示例3: 获取基金业绩 ==========
    print("\n" + "-" * 80)
    print("📍 示例3: 获取基金业绩表现")
    print("-" * 80)
    
    if funds:
        test_code = funds[0].fund_code
        
        print(f"\n基金: {test_code}")
        perf = adapter.get_fund_performance(test_code)
        
        if perf:
            print(f"\n收益表现:")
            print(f"  近1月: {perf.return_1m*100:+.2f}%")
            print(f"  近3月: {perf.return_3m*100:+.2f}%")
            print(f"  近6月: {perf.return_6m*100:+.2f}%")
            print(f"  近1年: {perf.return_1y*100:+.2f}%")
            print(f"  今年来: {perf.return_ytd*100:+.2f}%")
            print(f"\n风险指标:")
            print(f"  最大回撤: {perf.max_drawdown*100:.2f}%")
            print(f"  夏普比率: {perf.sharpe_ratio:.2f}")
            print(f"  波动率: {perf.volatility*100:.2f}%")
        else:
            print("  ⚠️ 未能获取业绩数据")
    
    # ========== 示例4: 获取基金持仓 ==========
    print("\n" + "-" * 80)
    print("📍 示例4: 获取基金持仓 (需配置正确季度)")
    print("-" * 80)
    
    if funds:
        test_code = funds[0].fund_code
        
        print(f"\n基金: {test_code}")
        print("前十大重仓股:")
        
        holdings = adapter.get_fund_holdings(test_code, quarter="2024Q4")
        if holdings:
            print(f"{'股票代码':<10} {'股票名称':<15} {'权重':<8} {'行业':<10}")
            print("-" * 50)
            for h in holdings[:10]:
                print(f"{h.stock_code:<10} {h.stock_name:<15} {h.weight*100:>6.2f}% {h.sector:<10}")
        else:
            print("  ⚠️ 未能获取持仓数据 (可能需要指定正确的季度)")
    
    # ========== 使用说明 ==========
    print("\n" + "=" * 80)
    print("📋 使用说明")
    print("=" * 80)
    print("""
1. 使用AkShare (默认，免费):
   - 自动使用AkShare获取数据
   - 无需配置，开箱即用
   - 数据更新频率：T+1

2. 使用同花顺iFinD (付费，更专业):
   - 设置环境变量: export THS_ACCESS_TOKEN='your_token'
   - 初始化时指定: get_fund_adapter(prefer_ths=True)
   - 数据更全面，包含更多指标

3. 自动降级:
   - iFinD不可用时自动使用AkShare
   - 都不可用时返回空数据

4. 数据缓存:
   - 默认缓存5分钟，减少API调用
   - 可配置缓存时间
""")
    
    print("=" * 80)


if __name__ == '__main__':
    demo_real_data()
