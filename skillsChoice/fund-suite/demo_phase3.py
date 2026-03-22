#!/usr/bin/env python3
"""
Phase 3 基金Skills套件完整演示
包含：fund-attribution-analysis, fund-holding-analyzer, fund-tax-optimizer
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-attribution-analysis/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-holding-analyzer/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-tax-optimizer/scripts')

from fund_attribution_analysis import AttributionAnalyzer
from fund_holding_analyzer import HoldingAnalyzer
from fund_tax_optimizer import TaxOptimizer


def demo_phase3():
    print("=" * 80)
    print("🎯 Phase 3: 基金分析类Skills 完整演示")
    print("=" * 80)
    print()
    
    # ========== Demo 1: 收益归因 ==========
    print("📊 Skill 7/10: fund-attribution-analysis (收益归因分析)")
    print("-" * 80)
    
    analyzer = AttributionAnalyzer()
    
    # Brinson归因
    print("\n【示例1】Brinson归因分析")
    portfolio_returns = {
        '科技': 0.12, '金融': 0.03, '消费': 0.08,
        '医药': 0.10, '制造': 0.06, '周期': 0.04
    }
    benchmark_returns = {
        '科技': 0.08, '金融': 0.04, '消费': 0.07,
        '医药': 0.09, '制造': 0.05, '周期': 0.05
    }
    portfolio_weights = {
        '科技': 0.30, '金融': 0.10, '消费': 0.20,
        '医药': 0.20, '制造': 0.15, '周期': 0.05
    }
    benchmark_weights = {
        '科技': 0.20, '金融': 0.20, '消费': 0.20,
        '医药': 0.15, '制造': 0.15, '周期': 0.10
    }
    
    brinson = analyzer.brinson_attribution(
        portfolio_returns, benchmark_returns,
        portfolio_weights, benchmark_weights
    )
    print(f"  组合收益: {brinson['returns']['portfolio']*100:.2f}%")
    print(f"  基准收益: {brinson['returns']['benchmark']*100:.2f}%")
    print(f"  超额收益: {brinson['returns']['excess']*100:+.2f}%")
    print(f"  归因分解:")
    print(f"    配置效应: {brinson['brinson_attribution']['allocation_effect']*100:+.2f}%")
    print(f"    选择效应: {brinson['brinson_attribution']['selection_effect']*100:+.2f}%")
    print(f"    交互效应: {brinson['brinson_attribution']['interaction_effect']*100:+.2f}%")
    print(f"  结论: {brinson['conclusion']}")
    
    # 因子归因
    print("\n【示例2】因子归因分析")
    fund_returns = [0.02, -0.01, 0.03, 0.01, 0.02, -0.02, 0.01, 0.03] * 5
    factor_returns = {
        'MKT': [0.015, -0.008, 0.025, 0.012, 0.018, -0.015, 0.008, 0.022] * 5,
        'HML': [-0.005, 0.003, -0.008, -0.002, -0.005, 0.005, -0.002, -0.008] * 5,
        'SMB': [0.008, -0.005, 0.012, 0.005, 0.008, -0.008, 0.005, 0.012] * 5,
    }
    factor = analyzer.factor_attribution(fund_returns, factor_returns)
    print(f"  模型R²: {factor['model_stats']['r_squared']:.1%}")
    print(f"  年化阿尔法: {factor['model_stats']['alpha_annual']:+.2f}%")
    print(f"  信息比率: {factor['model_stats']['information_ratio']:.2f}")
    print(f"  风格画像: {factor['style_profile'].get('dominant_style', 'N/A')}")
    
    print()
    
    # ========== Demo 2: 持仓分析 ==========
    print("📊 Skill 8/10: fund-holding-analyzer (持仓穿透分析)")
    print("-" * 80)
    
    holding_analyzer = HoldingAnalyzer()
    
    # 持仓分析
    print("\n【示例1】持仓集中度分析")
    report = holding_analyzer.analyze_holdings('000001', '2024Q4')
    conc = report['concentration']
    print(f"  CR5: {conc['cr5_pct']:.1f}% | CR10: {conc['cr10_pct']:.1f}%")
    print(f"  HHI: {conc['hhi']:.4f} (有效持仓: {conc['effective_holdings']})")
    print(f"  评级: {conc['rating']}")
    
    sector = report['sector_distribution']
    print(f"\n  行业分布Top3:")
    for sect, weight in list(sector['distribution'].items())[:3]:
        print(f"    {sect}: {weight*100:.1f}%")
    
    style = report['style_exposure']
    print(f"\n  风格分析:")
    print(f"    主导风格: {style['dominant_style']}")
    print(f"    市值: 大盘{style['market_cap']['large']*100:.0f}% / 中盘{style['market_cap']['mid']*100:.0f}% / 小盘{style['market_cap']['small']*100:.0f}%")
    
    # FOF穿透
    print("\n【示例2】FOF穿透分析")
    fof_holdings = [
        {'code': '000002', 'name': '华夏成长', 'weight': 0.25, 'type': 'equity'},
        {'code': '000003', 'name': '易方达蓝筹', 'weight': 0.20, 'type': 'equity'},
        {'code': '000004', 'name': '南方稳健', 'weight': 0.15, 'type': 'bond'},
        {'code': '000005', 'name': '招商产业债', 'weight': 0.15, 'type': 'bond'},
        {'code': 'CASH', 'name': '货币基金', 'weight': 0.10, 'type': 'cash'},
        {'code': 'OTHER', 'name': '其他', 'weight': 0.15, 'type': 'other'},
    ]
    fof_report = holding_analyzer.fof_lookthrough('FOF001', fof_holdings, max_depth=2)
    summary = fof_report['lookthrough_summary']
    print(f"  穿透后股票: {summary['stock_ratio']*100:.1f}%")
    print(f"  穿透后债券: {summary['bond_ratio']*100:.1f}%")
    print(f"  穿透后现金: {summary['cash_ratio']*100:.1f}%")
    print(f"  关联交易: {len(fof_report['related_party_check'])}项")
    
    print()
    
    # ========== Demo 3: 税务优化 ==========
    print("📊 Skill 9/10: fund-tax-optimizer (税务优化)")
    print("-" * 80)
    
    tax_optimizer = TaxOptimizer()
    
    # 赎回优化
    print("\n【示例1】赎回时机优化")
    from dataclasses import dataclass
    
    class HoldingLot:
        def __init__(self, lot_id, fund_code, fund_name, shares, cost_basis, purchase_date, current_nav):
            self.lot_id = lot_id
            self.fund_code = fund_code
            self.fund_name = fund_name
            self.shares = shares
            self.cost_basis = cost_basis
            self.purchase_date = purchase_date
            self.current_nav = current_nav
        
        def to_dict(self):
            return {
                'lot_id': self.lot_id,
                'fund_code': self.fund_code,
                'fund_name': self.fund_name,
                'shares': self.shares,
                'cost_basis': self.cost_basis,
                'purchase_date': self.purchase_date,
                'current_nav': self.current_nav
            }
        
        @property
        def current_value(self):
            return self.shares * self.current_nav
        
        @property
        def unrealized_gain(self):
            return self.shares * (self.current_nav - self.cost_basis)
        
        def holding_days(self, as_of_date):
            from datetime import datetime
            purchase = datetime.strptime(self.purchase_date, '%Y-%m-%d')
            as_of = datetime.strptime(as_of_date, '%Y-%m-%d')
            return (as_of - purchase).days
    
    holdings = [
        HoldingLot('LOT_20230115', '000001', '华夏成长', 8000, 1.20, '2023-01-15', 1.50),
        HoldingLot('LOT_20230601', '000002', '易方达蓝筹', 15000, 1.10, '2023-06-01', 1.20),
        HoldingLot('LOT_20240201', '000003', '中欧时代先锋', 14000, 1.45, '2024-02-01', 1.50),
    ]
    
    redemption = tax_optimizer.optimize_redemption(holdings, target_amount=50000, as_of_date='2026-03-21')
    print(f"  目标金额: ¥{redemption['target_amount']:,.0f}")
    print(f"  总赎回: ¥{redemption['summary']['total_redeemed']:,.0f}")
    print(f"  总费用: ¥{redemption['summary']['total_fee']:,.2f} ({redemption['summary']['weighted_fee_pct']:.2f}%)")
    print(f"  净到账: ¥{redemption['summary']['net_proceeds']:,.2f}")
    
    # 税收损失收割
    print("\n【示例2】税收损失收割")
    harvest_holdings = [
        HoldingLot('LOT_A', '000009', '广发科技创新', 10000, 1.80, '2024-08-01', 1.45),
        HoldingLot('LOT_B', '000010', '新能源基金', 5000, 1.50, '2024-10-01', 1.20),
        HoldingLot('LOT_C', '000001', '华夏成长', 8000, 1.20, '2023-01-15', 1.50),
    ]
    harvest = tax_optimizer.tax_loss_harvest(harvest_holdings, realized_gains=15000)
    print(f"  已实现收益: ¥{harvest['current_position']['realized_gains']:,.0f}")
    print(f"  可收割亏损: ¥{harvest['current_position']['total_unrealized_loss']:,.0f}")
    print(f"  建议收割: {len(harvest['recommended_harvests'])}笔")
    print(f"  潜在税收节省: ¥{harvest['tax_savings_analysis']['potential_savings']:,.2f}")
    
    # 分红对比
    print("\n【示例3】分红方式对比")
    dividend = tax_optimizer.compare_dividend_options(
        initial_amount=100000,
        annual_return=0.10,
        dividend_yield=0.03,
        years=5
    )
    cash = dividend['cash_dividend']
    reinvest = dividend['reinvest_dividend']
    print(f"  现金分红 5年后: ¥{cash['total_value']:,.0f} (总收益{cash['total_return']:.1f}%)")
    print(f"  红利再投资 5年后: ¥{reinvest['final_value']:,.0f} (总收益{reinvest['total_return']:.1f}%)")
    print(f"  差额: ¥{dividend['comparison']['value_difference']:,.0f} ({dividend['comparison']['percentage_difference']:+.2f}%)")
    print(f"  建议: {dividend['comparison']['advantage']}")
    
    print()
    
    # ========== 总结 ==========
    print("=" * 80)
    print("✅ Phase 3 分析类Skills 演示完成")
    print("=" * 80)
    print()
    print("📦 Phase 3 交付清单:")
    print()
    print("┌────┬───────────────────────────┬─────────────────────────────────────┐")
    print("│ #  │ Skill                     │ 核心功能                            │")
    print("├────┼───────────────────────────┼─────────────────────────────────────┤")
    print("│ 7  │ fund-attribution-analysis │ Brinson归因、因子归因、风格分析     │")
    print("│ 8  │ fund-holding-analyzer     │ 持仓集中度、FOF穿透、风格暴露       │")
    print("│ 9  │ fund-tax-optimizer        │ 赎回优化、税收损失收割、分红对比    │")
    print("└────┴───────────────────────────┴─────────────────────────────────────┘")
    print()
    print("📁 文件位置:")
    print("  • fund-attribution-analysis/")
    print("    - SKILL.md")
    print("    - scripts/fund_attribution_analysis.py")
    print("  • fund-holding-analyzer/")
    print("    - SKILL.md")
    print("    - scripts/fund_holding_analyzer.py")
    print("  • fund-tax-optimizer/")
    print("    - SKILL.md")
    print("    - scripts/fund_tax_optimizer.py")
    print()
    print("💡 使用示例:")
    print("  python3 fund_attribution_analysis.py --brinson")
    print("  python3 fund_holding_analyzer.py --fund 000001")
    print("  python3 fund_tax_optimizer.py --optimize --target 50000")


if __name__ == '__main__':
    demo_phase3()
