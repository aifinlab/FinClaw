#!/usr/bin/env python3
"""
fund-screener Skill 完整演示
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-screener/scripts')

from fund_screener import FundScreener


def demo_fund_screener():
    print("=" * 80)
    print("🏦 fund-screener Skill 完整演示")
    print("=" * 80)
    print()
    
    screener = FundScreener()
    
    # Demo 1: 基础筛选
    print("📊 Demo 1: 基础筛选 - 股票型基金")
    print("-" * 80)
    results = screener.screen(fund_type='股票型', limit=3)
    print(f"找到 {len(results)} 只股票型基金\n")
    for fund in results:
        print(f"  {fund['rank']}. {fund['fund_name']} ({fund['fund_code']})")
        print(f"     收益: {fund['return_1y']:.1f}% | 规模: {fund['scale']:.1f}亿 | 评级: {'⭐' * fund['rating']['overall']}")
    print()
    
    # Demo 2: 高级筛选
    print("📊 Demo 2: 高级筛选 - 高收益低波动基金")
    print("-" * 80)
    results = screener.screen(
        min_return_1y=20,
        max_volatility=20,
        min_scale=50,
        limit=5
    )
    print(f"筛选条件: 近1年收益>20%, 波动率<20%, 规模>50亿")
    print(f"找到 {len(results)} 只符合条件的基金\n")
    for fund in results:
        print(f"  {fund['rank']}. {fund['fund_name']}")
        print(f"     收益: {fund['return_1y']:.1f}% | 波动: {fund['volatility']:.1f}% | "
              f"规模: {fund['scale']:.1f}亿 | 夏普: {fund['sharpe_ratio']:.2f}")
    print()
    
    # Demo 3: 评级筛选
    print("📊 Demo 3: 评级筛选 - 五星基金")
    print("-" * 80)
    results = screener.screen(rating_min=5, limit=5)
    print(f"筛选条件: 综合评级5星")
    print(f"找到 {len(results)} 只五星基金\n")
    for fund in results:
        r = fund['rating']
        print(f"  {fund['rank']}. {fund['fund_name']}")
        print(f"     综合: {'⭐' * r['overall']} | 收益: {'⭐' * r['return_rating']} | "
              f"风险: {'⭐' * r['risk_rating']} | 费用: {'⭐' * r['fee_rating']}")
    print()
    
    # Demo 4: 基金对比
    print("📊 Demo 4: 基金对比分析")
    print("-" * 80)
    comparison = screener.compare_funds(['000001', '000002', '000003'])
    print(f"对比基金: 华夏成长、易方达蓝筹、中欧时代\n")
    
    print(f"{'指标':<15} {'华夏成长':<12} {'易方达蓝筹':<12} {'中欧时代':<12}")
    print("-" * 55)
    
    metrics = [
        ('近1年收益', 'return_1y', '%'),
        ('近3年收益', 'return_3y', '%'),
        ('波动率', 'volatility', '%'),
        ('夏普比率', 'sharpe_ratio', ''),
        ('最大回撤', 'max_drawdown', '%'),
        ('基金规模', 'scale', '亿'),
    ]
    
    for label, key, unit in metrics:
        values = [f"{f[key]:.2f}{unit}" for f in comparison['funds']]
        print(f"{label:<15} {values[0]:<12} {values[1]:<12} {values[2]:<12}")
    print()
    
    # Demo 5: 基金详情
    print("📊 Demo 5: 基金详情分析")
    print("-" * 80)
    detail = screener.get_fund_detail('000007')
    print(f"基金名称: {detail['fund_name']}")
    print(f"基金代码: {detail['fund_code']}")
    print(f"基金类型: {detail['fund_type']}")
    print(f"\n业绩表现:")
    print(f"  近1年收益: {detail['return_1y']:+.2f}%")
    print(f"  近3年收益: {detail['return_3y']:+.2f}%")
    print(f"  夏普比率: {detail['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {detail['max_drawdown']:.2f}%")
    print(f"\n五星评级: {'⭐' * detail['rating']['overall']}")
    
    if 'analysis' in detail:
        print(f"\n分析建议:")
        for strength in detail['analysis']['strengths']:
            print(f"  ✅ {strength}")
    print()
    
    # 总结
    print("=" * 80)
    print("✅ fund-screener Skill 演示完成")
    print("=" * 80)
    print()
    print("📁 Skill文件位置:")
    print("  • SKILL.md: finclaw/skills/fund-suite/fund-screener/SKILL.md")
    print("  • 核心脚本: finclaw/skills/fund-suite/fund-screener/scripts/fund_screener.py")
    print()
    print("🔧 核心功能:")
    print("  ✓ 多维度基金筛选")
    print("  ✓ 五星评级体系")
    print("  ✓ 同类排名对比")
    print("  ✓ 基金详情分析")
    print("  ✓ 智能对比功能")
    print()
    print("💡 使用方式:")
    print("  python3 fund_screener.py --type 混合型 --min-return 20")
    print("  python3 fund_screener.py --code 000001")
    print("  python3 fund_screener.py --compare 000001,000002")


if __name__ == '__main__':
    demo_fund_screener()
