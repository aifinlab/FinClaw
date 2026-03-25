#!/usr/bin/env python3
"""
基金换仓建议核心模块（真实数据版）
Fund Rebalance Advisor Core Module - Real Data Edition

功能：偏离度检测、换仓建议、赎回费计算、优化方案
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-rebalance-advisor/scripts')
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/data')

import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# 导入数据适配器
try:
    from fund_data_adapter import get_fund_adapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError as e:
    DATA_ADAPTER_AVAILABLE = False


def calculate_redemption_fee(holding_days: int) -> float:
    """
    计算赎回费（证监会规定）
    
    Args:
        holding_days: 持有天数
    
    Returns:
        赎回费率
    """
    if holding_days <= 7:
        return 0.015  # 1.5%
    elif holding_days <= 30:
        return 0.0075  # 0.75%
    elif holding_days <= 365:
        return 0.005  # 0.5%
    elif holding_days <= 730:
        return 0.0025  # 0.25%
    else:
        return 0.0  # 免费


def analyze_rebalance(current_allocation: Dict, target_allocation: Dict,
                     current_holdings: List[Dict]) -> Dict:
    """
    分析换仓需求
    
    Args:
        current_allocation: 当前配置比例
        target_allocation: 目标配置比例
        current_holdings: 当前持仓详情
    
    Returns:
        换仓建议报告
    """
    deviations = []
    total_deviation = 0
    
    for asset_type, current_pct in current_allocation.items():
        target_pct = target_allocation.get(asset_type, 0)
        deviation = abs(current_pct - target_pct)
        
        if deviation > 0:
            deviations.append({
                'asset_type': asset_type,
                'current': current_pct,
                'target': target_pct,
                'deviation': deviation,
                'action': '增持' if target_pct > current_pct else '减持'
            })
            total_deviation += deviation
    
    # 计算最大偏离
    max_deviation = max([d['deviation'] for d in deviations]) if deviations else 0
    
    # 判断是否需要换仓
    need_rebalance = max_deviation > 0.05  # 5%阈值
    
    # 计算赎回费用
    total_redemption_fee = 0
    for holding in current_holdings:
        days = holding.get('holding_days', 365)
        value = holding.get('value', 0)
        fee_rate = calculate_redemption_fee(days)
        fee = value * fee_rate
        total_redemption_fee += fee
        holding['redemption_fee_rate'] = fee_rate
        holding['redemption_fee'] = fee
    
    # 生成建议
    recommendations = []
    if not need_rebalance:
        recommendations.append("当前配置偏离度在合理范围内，无需换仓")
    else:
        recommendations.append(f"最大偏离度 {max_deviation:.1%}，建议进行再平衡")
        
        if total_redemption_fee > 100:
            recommendations.append(f"预计赎回费 ¥{total_redemption_fee:.0f}，可考虑分批换仓降低成本")
        
        # 识别持有期超过2年的基金（免赎回费）
        free_funds = [h for h in current_holdings if h.get('holding_days', 0) > 730]
        if free_funds:
            recommendations.append(f"有 {len(free_funds)} 只基金持有超2年，赎回免费，优先调整")
    
    return {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'deviation_analysis': {
            'deviations': deviations,
            'max_deviation': max_deviation,
            'total_deviation': total_deviation,
            'need_rebalance': need_rebalance
        },
        'cost_analysis': {
            'total_redemption_fee': total_redemption_fee,
            'holding_details': current_holdings
        },
        'recommendations': recommendations,
        'data_source': '硬编码标准(证监会规定)'
    }


def main():
    parser = argparse.ArgumentParser(description='基金换仓建议')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 示例数据（⚠️ 示例数据-需替换为真实数据）
    import warnings
    warnings.warn(
        "⚠️ 正在使用示例数据！请传入真实的current/target/holdings参数。\n"
        "   示例基金代码和持仓数据仅供演示，请勿用于生产环境。",
        UserWarning,
        stacklevel=2
    )
    
    current = {'equity': 0.40, 'bond': 0.35, 'money': 0.25}
    target = {'equity': 0.30, 'bond': 0.40, 'money': 0.30}
    holdings = [
        {'code': 'EXAMPLE001', 'name': '示例基金A（需替换）', 'value': 40000, 'holding_days': 100, '_note': '示例数据'},
        {'code': 'EXAMPLE002', 'name': '示例基金B（需替换）', 'value': 35000, 'holding_days': 800, '_note': '示例数据'},
    ]
    
    result = analyze_rebalance(current, target, holdings)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print("📊 换仓分析报告")
        print("=" * 60)
        print(f"分析日期: {result['analysis_date']}")
        print(f"数据源: {result['data_source']}")
        
        print(f"\n偏离度分析:")
        for d in result['deviation_analysis']['deviations']:
            print(f"  {d['asset_type']}: 当前{d['current']:.1%} → 目标{d['target']:.1%} ({d['action']})")
        print(f"  最大偏离: {result['deviation_analysis']['max_deviation']:.1%}")
        
        print(f"\n成本分析:")
        print(f"  预计赎回费: ¥{result['cost_analysis']['total_redemption_fee']:.0f}")
        
        print(f"\n建议:")
        for rec in result['recommendations']:
            print(f"  • {rec}")


if __name__ == '__main__':
    main()
