#!/usr/bin/env python3
"""
Phase 2 基金Skills套件完整演示
包含：fund-portfolio-allocation, fund-sip-planner, fund-rebalance-advisor
"""

import sys
import os

# 添加路径
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-portfolio-allocation/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-sip-planner/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-rebalance-advisor/scripts')

from fund_portfolio_allocation import PortfolioAllocator
from fund_sip_planner import SIPPlanner
from fund_rebalance_advisor import RebalanceAdvisor


def demo_phase2():
    print("=" * 80)
    print("🎯 Phase 2: 基金配置类Skills 完整演示")
    print("=" * 80)
    print()
    
    # ========== Demo 1: 组合配置 ==========
    print("📊 Skill 1/3: fund-portfolio-allocation (基金组合配置)")
    print("-" * 80)
    
    allocator = PortfolioAllocator()
    
    # SAA配置
    print("\n【示例1】战略资产配置 (SAA)")
    saa_report = allocator.allocate(
        target='稳健增长',
        amount=1000000,
        risk_profile='R3',
        strategy='saa'
    )
    print(f"  风险等级: {saa_report['risk_description']}")
    print(f"  预期年化收益: {saa_report['expected_metrics']['expected_return']:.1%}")
    print(f"  预期波动率: {saa_report['expected_metrics']['expected_volatility']:.1%}")
    print(f"  配置:")
    for asset_type, data in saa_report['allocation']['by_type'].items():
        type_name = {'equity': '股票型', 'hybrid': '混合型', 'bond': '债券型', 'money': '货币型'}.get(asset_type, asset_type)
        print(f"    {type_name}: {data['weight']:.1%} (¥{data['amount']:,.0f})")
    
    # 风险平价配置
    print("\n【示例2】风险平价配置")
    rp_report = allocator.allocate(
        target='风险均衡',
        amount=1000000,
        risk_profile='R3',
        strategy='risk-parity'
    )
    print(f"  策略: {rp_report['strategy']}")
    comp = rp_report.get('comparison', {})
    if comp:
        print(f"  与传统60/40对比:")
        print(f"    风险平价波动率: {comp['risk_parity']['volatility']:.1%}")
        print(f"    传统配置波动率: {comp['traditional_60_40']['volatility']:.1%}")
    
    print()
    
    # ========== Demo 2: 定投规划 ==========
    print("📊 Skill 2/3: fund-sip-planner (基金定投规划)")
    print("-" * 80)
    
    planner = SIPPlanner()
    
    # 定投计划
    print("\n【示例1】定投计划设计")
    plan = planner.create_plan(
        target_amount=100000,
        monthly_amount=2000,
        years=5,
        strategy='fixed'
    )
    print(f"  目标金额: ¥{plan['target_amount']:,.0f}")
    print(f"  每月定投: ¥{plan['monthly_amount']:,.0f}")
    print(f"  投资年限: {plan['years']}年")
    proj = plan['projections']
    print(f"  预期收益: ¥{proj['projected_profit']:,.0f} ({proj['return_rate']:.1f}%)")
    target = plan['target_analysis']
    if target['can_reach_target']:
        print(f"  预计{target['months_to_target']}个月达成目标")
    
    # 智能定投回测
    print("\n【示例2】均线定投策略回测")
    backtest = planner.backtest(
        fund_code='000001',
        strategy='ma',
        base_amount=1000,
        years=3
    )
    fixed = backtest['comparison']['fixed']
    smart = backtest['comparison']['smart']
    print(f"  固定定投收益: {fixed['return_rate']:.1f}%")
    print(f"  均线定投收益: {smart['return_rate']:.1f}%")
    print(f"  平均成本对比: {fixed['avg_cost']:.4f} vs {smart['avg_cost']:.4f}")
    
    print()
    
    # ========== Demo 3: 换仓建议 ==========
    print("📊 Skill 3/3: fund-rebalance-advisor (基金换仓建议)")
    print("-" * 80)
    
    advisor = RebalanceAdvisor()
    
    # 示例组合
    sample_portfolio = {
        'total_value': 1000000,
        'holdings': [
            {'fund_code': '000003', 'fund_name': '中欧时代先锋', 'fund_type': 'equity', 'value': 200000, 'holding_days': 800, 'cost_basis': 180000},
            {'fund_code': '000009', 'fund_name': '广发科技创新', 'fund_type': 'equity', 'value': 220000, 'holding_days': 400, 'cost_basis': 140000},
            {'fund_code': '000001', 'fund_name': '华夏成长混合', 'fund_type': 'hybrid', 'value': 280000, 'holding_days': 1000, 'cost_basis': 160000},
            {'fund_code': '000008', 'fund_name': '南方稳健成长', 'fund_type': 'bond', 'value': 220000, 'holding_days': 500, 'cost_basis': 210000},
            {'fund_code': '000012', 'fund_name': '天弘余额宝', 'fund_type': 'money', 'value': 80000, 'holding_days': 300, 'cost_basis': 80000},
        ]
    }
    
    target_allocation = {
        'equity': 0.30,
        'hybrid': 0.30,
        'bond': 0.30,
        'money': 0.10
    }
    
    # 偏离度检测
    print("\n【示例1】偏离度检测")
    deviation = advisor.check_deviation(sample_portfolio, target_allocation)
    print(f"  最大偏离度: {deviation['deviation_analysis']['max_deviation_pct']:.1f}%")
    print(f"  平均偏离度: {deviation['deviation_analysis']['avg_deviation_pct']:.1f}%")
    print(f"  需要再平衡: {'是' if deviation['deviation_analysis']['needs_rebalance'] else '否'}")
    
    # 换仓建议
    print("\n【示例2】换仓建议")
    advice = advisor.generate_advice(sample_portfolio, target_allocation)
    summary = advice['rebalance_summary']
    print(f"  总卖出: ¥{summary['total_sell']:,.0f}")
    print(f"  总买入: ¥{summary['total_buy']:,.0f}")
    costs = advice['cost_analysis']
    print(f"  预估成本: ¥{costs['total_cost']:,.2f} ({costs['cost_percentage']:.3f}%)")
    plan = advice['execution_plan']
    print(f"  执行方式: {'一次性' if plan['method'] == 'one_time' else '分批'} ({plan['batches']}批)")
    
    print()
    
    # ========== 总结 ==========
    print("=" * 80)
    print("✅ Phase 2 配置类Skills 演示完成")
    print("=" * 80)
    print()
    print("📦 Phase 2 交付清单:")
    print()
    print("┌────┬───────────────────────────┬─────────────────────────────────────┐")
    print("│ #  │ Skill                     │ 核心功能                            │")
    print("├────┼───────────────────────────┼─────────────────────────────────────┤")
    print("│ 4  │ fund-portfolio-allocation │ SAA/TAA/Markowitz/风险平价配置     │")
    print("│ 5  │ fund-sip-planner          │ 定投计划/智能定投(均线/估值/趋势)   │")
    print("│ 6  │ fund-rebalance-advisor    │ 偏离度检测/换仓建议/成本控制        │")
    print("└────┴───────────────────────────┴─────────────────────────────────────┘")
    print()
    print("📁 文件位置:")
    print("  • fund-portfolio-allocation/")
    print("    - SKILL.md")
    print("    - scripts/fund_portfolio_allocation.py")
    print("  • fund-sip-planner/")
    print("    - SKILL.md")
    print("    - scripts/fund_sip_planner.py")
    print("  • fund-rebalance-advisor/")
    print("    - SKILL.md")
    print("    - scripts/fund_rebalance_advisor.py")
    print()
    print("💡 使用示例:")
    print("  python3 fund_portfolio_allocation.py --target 稳健增长 --amount 1000000 --risk R3")
    print("  python3 fund_sip_planner.py --target 100000 --monthly 2000 --years 5")
    print("  python3 fund_rebalance_advisor.py --check")


if __name__ == '__main__':
    demo_phase2()
