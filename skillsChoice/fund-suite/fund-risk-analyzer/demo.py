#!/usr/bin/env python3
"""
fund-risk-analyzer Skill 完整演示
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-risk-analyzer/scripts')

from fund_risk_analyzer import FundRiskAnalyzer


def demo_fund_risk_analyzer():
    print("=" * 80)
    print("⚠️ fund-risk-analyzer Skill 完整演示")
    print("=" * 80)
    print()
    
    analyzer = FundRiskAnalyzer()
    
    # Demo 1: 全面风险分析
    print("📊 Demo 1: 全面风险分析")
    print("-" * 80)
    report = analyzer.analyze('000001')
    print(f"基金: {report['fund_name']}")
    print(f"风险等级: {report['risk_assessment']['overall_risk_level']}")
    print(f"风险评分: {report['risk_assessment']['risk_score']}/100")
    print()
    
    m = report['risk_metrics']
    print(f"风险调整收益:")
    print(f"  夏普比率: {m['sharpe_ratio']:.2f}")
    print(f"  索提诺比率: {m['sortino_ratio']:.2f}")
    print(f"  卡玛比率: {m['calmar_ratio']:.2f}")
    
    print(f"\n极端风险:")
    print(f"  95% VaR: {m['var_95']:+.2f}%")
    print(f"  99% VaR: {m['var_99']:+.2f}%")
    print(f"  最大回撤: {m['max_drawdown']:+.2f}%")
    
    print(f"\n市场风险:")
    print(f"  Beta: {m['beta']:.2f}")
    print(f"  Alpha: {m['alpha']:+.2f}%")
    print()
    
    # Demo 2: VaR计算
    print("📊 Demo 2: VaR计算（多种方法）")
    print("-" * 80)
    
    for method in ['historical', 'parametric', 'monte_carlo']:
        var_result = analyzer.calculate_var('000001', confidence=0.95, method=method)
        print(f"{method:12s}: 日度VaR = {var_result.get('daily_var', 'N/A')}")
    print()
    
    # Demo 3: 风险对比
    print("📊 Demo 3: 多基金风险对比")
    print("-" * 80)
    comparison = analyzer.compare_risk(['000001', '000002', '000003'])
    
    print(f"{'基金':<15} {'夏普':<8} {'索提诺':<8} {'VaR95':<8} {'回撤':<8}")
    print("-" * 60)
    for fund in comparison['funds']:
        m = fund['risk_metrics']
        print(f"{fund['fund_name'][:12]:<15} {m['sharpe_ratio']:<8.2f} "
              f"{m['sortino_ratio']:<8.2f} {m['var_95']:<8.2f} {m['max_drawdown']:<8.2f}")
    print()
    
    # Demo 4: 风险预警
    print("📊 Demo 4: 风险预警检查")
    print("-" * 80)
    
    high_risk_funds = ['000007', '000009']  # 高风险基金
    for code in high_risk_funds:
        alerts = analyzer.check_risk_alerts(code)
        info = analyzer.fund_info.get(code, {})
        print(f"\n{info.get('name', code)} ({code}):")
        if alerts:
            for alert in alerts:
                emoji = "🔴" if alert.get('level') == 'high' else "🟡"
                print(f"  {emoji} {alert.get('message', '')}")
        else:
            print("  ✅ 无预警")
    print()
    
    # Demo 5: 不同风险等级基金
    print("📊 Demo 5: 不同风险等级基金对比")
    print("-" * 80)
    
    risk_levels = [
        ('000008', '低风险'),   # 南方稳健
        ('000002', '中低风险'), # 易方达蓝筹
        ('000001', '中等风险'), # 华夏成长
        ('000007', '中高风险'), # 招商白酒
        ('000009', '高风险'),   # 广发科创
    ]
    
    print(f"{'基金':<15} {'类型':<10} {'风险等级':<10} {'波动率':<8} {'VaR':<8}")
    print("-" * 65)
    for code, expected_level in risk_levels:
        report = analyzer.analyze(code)
        m = report['risk_metrics']
        print(f"{report['fund_name'][:12]:<15} {expected_level:<10} "
              f"{report['risk_assessment']['overall_risk_level']:<10} "
              f"{m['volatility']:<8.1f}% {m['var_95']:<8.2f}%")
    print()
    
    # 总结
    print("=" * 80)
    print("✅ fund-risk-analyzer Skill 演示完成")
    print("=" * 80)
    print()
    print("📁 Skill文件位置:")
    print("  • SKILL.md: finclaw/skills/fund-suite/fund-risk-analyzer/SKILL.md")
    print("  • 核心脚本: finclaw/skills/fund-suite/fund-risk-analyzer/scripts/fund_risk_analyzer.py")
    print()
    print("🔧 核心功能:")
    print("  ✓ VaR/CVaR计算（历史/参数/蒙特卡洛）")
    print("  ✓ 夏普/索提诺/特雷诺/卡玛比率")
    print("  ✓ Beta/Alpha/R²市场风险分析")
    print("  ✓ 最大回撤/回撤持续期分析")
    print("  ✓ 波动率分解（上行/下行/系统/非系统）")
    print("  ✓ 尾部风险（偏度/峰度）")
    print("  ✓ 风险等级评估与预警")
    print()
    print("💡 使用方式:")
    print("  python3 fund_risk_analyzer.py --code 000001")
    print("  python3 fund_risk_analyzer.py --code 000001 --var --confidence 0.95")
    print("  python3 fund_risk_analyzer.py --compare 000001,000002,000003")
    print("  python3 fund_risk_analyzer.py --code 000001 --alert")


if __name__ == '__main__':
    demo_fund_risk_analyzer()
