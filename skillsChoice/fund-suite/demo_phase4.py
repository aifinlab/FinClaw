#!/usr/bin/env python3
"""
Phase 4 基金Skills套件演示
fund-monitor: 组合监控预警
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-monitor/scripts')

from fund_monitor import FundMonitor


def demo_phase4():
    print("=" * 80)
    print("🎯 Phase 4: 基金监控类Skills 演示")
    print("=" * 80)
    print()
    
    monitor = FundMonitor()
    
    # 添加示例组合
    sample_holdings = [
        {'fund_code': '000001', 'fund_name': '华夏成长', 'fund_type': 'equity', 'weight': 0.25, 'value': 25000},
        {'fund_code': '000002', 'fund_name': '易方达蓝筹', 'fund_type': 'equity', 'weight': 0.20, 'value': 20000},
        {'fund_code': '000003', 'fund_name': '中欧时代', 'fund_type': 'equity', 'weight': 0.15, 'value': 15000},
        {'fund_code': '000004', 'fund_name': '南方稳健', 'fund_type': 'bond', 'weight': 0.20, 'value': 20000},
        {'fund_code': '000005', 'fund_name': '招商产业债', 'fund_type': 'bond', 'weight': 0.15, 'value': 15000},
        {'fund_code': 'CASH', 'fund_name': '货币基金', 'fund_type': 'money', 'weight': 0.05, 'value': 5000},
    ]
    
    monitor.add_portfolio('PF001', sample_holdings, target_return=0.10)
    
    # 监控状态检查
    print("📊 Skill 10/10: fund-monitor (组合监控预警)")
    print("-" * 80)
    
    print("\n【示例1】实时监控状态检查")
    status = monitor.check_alerts('PF001')
    print(f"  组合ID: {status['portfolio_id']}")
    print(f"  状态: {status['status_emoji']} {status['status'].upper()}")
    print(f"  组合价值: ¥{status['portfolio_value']:,.0f}")
    print(f"  累计收益: {status['portfolio_return_pct']:+.2f}%")
    print(f"  当前回撤: {status['drawdown_pct']:.2f}%")
    print(f"  活跃预警: {status['alerts_count']}个")
    
    metrics = status['metrics']
    print(f"  风险指标: 夏普{metrics['sharpe_ratio']:.2f} | 波动率{metrics['volatility_pct']:.1f}% | VaR{metrics['var_95_pct']:.2f}%")
    
    # 周报生成
    print("\n【示例2】定期报告生成")
    report = monitor.generate_report('PF001', period='weekly')
    returns = report['returns']
    print(f"  本周收益: {returns.get('weekly_pct', 0):+.2f}%")
    print(f"  本月收益: {returns.get('monthly_pct', 0):+.2f}%")
    print(f"  本年收益: {returns.get('ytd_pct', 0):+.2f}%")
    
    bench = report['benchmark_comparison']
    print(f"  超额收益(YTD): {bench.get('excess_ytd', 0)*100:+.2f}%")
    print(f"  排名: {report['ranking']['current']}/{report['ranking']['total']} ({report['ranking']['percentile']})")
    
    print()
    
    # ========== 总结 ==========
    print("=" * 80)
    print("✅ Phase 4 监控类Skills 演示完成")
    print("=" * 80)
    print()
    print("📦 Phase 4 交付清单:")
    print()
    print("┌────┬──────────────────┬─────────────────────────────────────┐")
    print("│ #  │ Skill            │ 核心功能                            │")
    print("├────┼──────────────────┼─────────────────────────────────────┤")
    print("│ 10 │ fund-monitor     │ 实时监控/多维度预警/定期报告/业绩跟踪 │")
    print("└────┴──────────────────┴─────────────────────────────────────┘")
    print()
    print("📁 文件位置:")
    print("  • fund-monitor/")
    print("    - SKILL.md")
    print("    - scripts/fund_monitor.py")
    print()
    print("💡 使用示例:")
    print("  python3 fund_monitor.py --check")
    print("  python3 fund_monitor.py --report --period weekly")


if __name__ == '__main__':
    demo_phase4()
