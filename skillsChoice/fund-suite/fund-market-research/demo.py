#!/usr/bin/env python3
"""
fund-market-research Skill 完整演示
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-market-research/scripts')

from fund_market_research import FundMarketResearch


def demo_fund_market_research():
    print("=" * 80)
    print("📈 fund-market-research Skill 完整演示")
    print("=" * 80)
    print()
    
    research = FundMarketResearch()
    
    # Demo 1: 市场概览
    print("📊 Demo 1: 基金市场概览")
    print("-" * 80)
    overview = research.get_overview()
    print(f"报告日期: {overview['report_date']}")
    print(f"基金总数: {overview['market_overview']['total_funds']:,}只")
    print(f"管理规模: {overview['market_overview']['total_scale']:.2f}万亿")
    print(f"年内新发: {overview['market_trends']['new_funds_30d']}只")
    print()
    
    # Demo 2: 资金流向
    print("📊 Demo 2: 近30天资金流向")
    print("-" * 80)
    flow = research.get_fund_flow(days=30)
    print(f"总体净流向: {flow['overall']['net_inflow']:+.1f}亿")
    print(f"  - 流入: {flow['overall']['inflow_amount']:.1f}亿")
    print(f"  - 流出: {flow['overall']['outflow_amount']:.1f}亿")
    print(f"\n分类流向:")
    for key, cat in flow['by_category'].items():
        status = "🟢流入" if cat['net_inflow'] > 0 else "🔴流出"
        print(f"  {cat['name']:<8}: {cat['net_inflow']:>+8.1f}亿 {status}")
    print()
    
    # Demo 3: 热门板块
    print("📊 Demo 3: 热门板块追踪")
    print("-" * 80)
    sectors = research.get_hot_sectors(top_n=5)
    print(f"{'排名':<4} {'板块':<12} {'基金数':<8} {'规模(亿)':<10} {'30天收益':<10} {'热度':<8}")
    print("-" * 60)
    for i, sector in enumerate(sectors['sector_ranking'], 1):
        heat_fire = "🔥" * (sector['heat'] // 30 + 1)
        print(f"{i:<4} {sector['name']:<12} {sector['fund_count']:<8} "
              f"{sector['scale']:<10} {sector['return_30d']:>+8.1f}% {heat_fire:<8}")
    print()
    
    # Demo 4: 发行日历
    print("📊 Demo 4: 基金发行日历")
    print("-" * 80)
    calendar = research.get_calendar(days=30)
    print(f"未来30天待发基金: {calendar['statistics']['total_upcoming']}只")
    print(f"目标募集规模: {calendar['statistics']['total_target_scale']:.0f}亿")
    print(f"\n待发基金:")
    for fund in calendar['upcoming_funds']:
        print(f"  • {fund['fund_name']} ({fund['company']})")
        print(f"    发行期: {fund['start_date']} ~ {fund['end_date']}")
        print(f"    目标规模: {fund['target_scale']} | 主题: {fund['investment_theme']}")
    print()
    
    # Demo 5: 市场情绪
    print("📊 Demo 5: 市场情绪指数")
    print("-" * 80)
    sentiment = research.get_sentiment_index()
    print(f"情绪指数: {sentiment['sentiment_index']:.1f} {sentiment['emoji']}")
    print(f"情绪状态: {sentiment['sentiment_level']}")
    print(f"\n解读: {sentiment['interpretation']}")
    print(f"\n因子分解:")
    for factor, value in sentiment['factors'].items():
        print(f"  {factor:<20} {value:>5.1f}")
    print()
    
    # Demo 6: 收益分布
    print("📊 Demo 6: 基金收益分布")
    print("-" * 80)
    dist = research.get_returns_distribution()
    print(f"年内收益分布:")
    ytd = dist['distributions']['ytd']
    print(f"  平均值: {ytd['avg']:+.1f}%")
    print(f"  中位数: {ytd['median']:+.1f}%")
    print(f"  最大值: {ytd['max']:+.1f}%")
    print(f"  最小值: {ytd['min']:+.1f}%")
    print(f"\n收益区间分布:")
    for range_name, count in ytd['distribution'].items():
        bar = "█" * int(count / 200)
        print(f"  {range_name:<10} {count:>5}只 {bar}")
    print()
    
    # 总结
    print("=" * 80)
    print("✅ fund-market-research Skill 演示完成")
    print("=" * 80)
    print()
    print("📁 Skill文件位置:")
    print("  • SKILL.md: finclaw/skills/fund-suite/fund-market-research/SKILL.md")
    print("  • 核心脚本: finclaw/skills/fund-suite/fund-market-research/scripts/fund_market_research.py")
    print()
    print("🔧 核心功能:")
    print("  ✓ 市场规模统计（总数/规模/类别分布）")
    print("  ✓ 资金流向分析（总体/分类/热门流入流出）")
    print("  ✓ 热门板块追踪（行业/风格/区域主题）")
    print("  ✓ 发行日历（待发基金/统计信息）")
    print("  ✓ 市场情绪指数（多因子综合评估）")
    print("  ✓ 收益分布分析（区间分布/统计指标）")
    print()
    print("💡 使用方式:")
    print("  python3 fund_market_research.py --overview")
    print("  python3 fund_market_research.py --flow --period 30d")
    print("  python3 fund_market_research.py --hot-sectors")
    print("  python3 fund_market_research.py --calendar --days 30")
    print("  python3 fund_market_research.py --sentiment")


if __name__ == '__main__':
    demo_fund_market_research()
