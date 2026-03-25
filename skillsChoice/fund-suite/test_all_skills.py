#!/usr/bin/env python3
"""
测试重写后的4个Fund Suite Skills
"""

import sys
import os

# 测试fund-risk-analyzer
print("=" * 60)
print("1. Testing fund-risk-analyzer")
print("=" * 60)
sys.path.insert(0, '/root/.openclaw/workspace/skillsChoice/fund-suite/fund-risk-analyzer/scripts')
try:
    import fund_risk_analyzer as fra
    analyzer = fra.FundRiskAnalyzer()
    report = analyzer.analyze('000001', period=60)
    print(f"✅ Fund Risk Analyzer loaded successfully")
    print(f"   Data Source: {report.get('data_source', 'N/A')}")
    print(f"   Data Quality: {report.get('data_quality', 'N/A')}")
    print(f"   Has VaR: {report['risk_metrics']['var_95'] != 0}")
    print(f"   Has CVaR: {report['risk_metrics']['cvar_95'] != 0}")
    print(f"   Has Drawdown: {report['risk_metrics']['max_drawdown'] != 0}")
except Exception as e:
    print(f"❌ Error: {e}")

# 测试fund-rebalance-advisor
print("\n" + "=" * 60)
print("2. Testing fund-rebalance-advisor")
print("=" * 60)
sys.path.insert(0, '/root/.openclaw/workspace/skillsChoice/fund-suite/fund-rebalance-advisor/scripts')
try:
    import fund_rebalance_advisor as fra
    advisor = fra.RebalanceAdvisor()
    portfolio, target = advisor.get_sample_portfolio()
    report = advisor.check_deviation(portfolio, target)
    print(f"✅ Fund Rebalance Advisor loaded successfully")
    print(f"   Data Source: {report.get('data_source', 'N/A')}")
    print(f"   Data Quality: {report.get('data_quality', 'N/A')}")
    print(f"   Has Deviation Analysis: {'deviation_analysis' in report}")
except Exception as e:
    print(f"❌ Error: {e}")

# 测试fund-attribution-analysis
print("\n" + "=" * 60)
print("3. Testing fund-attribution-analysis")
print("=" * 60)
sys.path.insert(0, '/root/.openclaw/workspace/skillsChoice/fund-suite/fund-attribution-analysis/scripts')
try:
    import fund_attribution_analysis as faa
    analyzer = faa.AttributionAnalyzer()
    report = analyzer.brinson_attribution('000001')
    print(f"✅ Fund Attribution Analysis loaded successfully")
    print(f"   Data Source: {report.get('data_source', 'N/A')}")
    print(f"   Data Quality: {report.get('data_quality', 'N/A')}")
    print(f"   Has Brinson: {'brinson_attribution' in report}")
    print(f"   Has Sectors: {'sector_attribution' in report}")
except Exception as e:
    print(f"❌ Error: {e}")

# 测试fund-tax-optimizer
print("\n" + "=" * 60)
print("4. Testing fund-tax-optimizer")
print("=" * 60)
sys.path.insert(0, '/root/.openclaw/workspace/skillsChoice/fund-suite/fund-tax-optimizer/scripts')
try:
    import fund_tax_optimizer as fto
    optimizer = fto.TaxOptimizer()
    holdings = optimizer.get_sample_holdings()
    report = optimizer.optimize_redemption(holdings, 50000)
    print(f"✅ Fund Tax Optimizer loaded successfully")
    print(f"   Data Source: {report.get('data_source', 'N/A')}")
    print(f"   Data Quality: {report.get('data_quality', 'N/A')}")
    print(f"   Has Recommendations: {len(report.get('recommendations', [])) > 0}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("All Skills Test Completed!")
print("=" * 60)
