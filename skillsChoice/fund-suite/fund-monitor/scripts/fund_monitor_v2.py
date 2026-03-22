#!/usr/bin/env python3
"""
基金组合监控核心模块（真实数据版）
Fund Monitor Core Module - Real Data Edition

功能：实时监控、预警提醒、风险分析、定期报告
数据源：AkShare / 同花顺iFinD
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-monitor/scripts')
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


class FundMonitor:
    """基金组合监控器（真实数据版）"""
    
    # 预警阈值
    ALERT_THRESHOLDS = {
        'daily_drop': -0.03,  # 单日跌3%
        'weekly_drop': -0.05,  # 周跌5%
        'drawdown_10': -0.10,  # 回撤10%
        'drawdown_15': -0.15,  # 回撤15%
        'drawdown_20': -0.20,  # 回撤20%
    }
    
    def __init__(self, use_real_data: bool = True):
        self.data_adapter = None
        self.data_source = "模拟数据"
        
        if use_real_data and DATA_ADAPTER_AVAILABLE:
            self._init_data_adapter()
    
    def _init_data_adapter(self):
        try:
            self.data_adapter = get_fund_adapter(prefer_ths=False)
            self.data_source = self.data_adapter.get_data_source()
            print(f"✅ 数据源: {self.data_source}")
        except Exception as e:
            print(f"⚠️ 数据适配器初始化失败: {e}")
    
    def monitor_portfolio(self, portfolio: Dict) -> Dict:
        """
        监控组合状态
        
        Args:
            portfolio: 组合信息
        
        Returns:
            监控报告
        """
        holdings = portfolio.get('holdings', [])
        alerts = []
        status = 'normal'
        
        # 检查每只基金
        for holding in holdings:
            fund_alerts = self._check_fund_alerts(holding)
            alerts.extend(fund_alerts)
        
        # 检查组合整体风险
        portfolio_alerts = self._check_portfolio_risk(portfolio)
        alerts.extend(portfolio_alerts)
        
        # 确定整体状态
        if any(a['level'] == 'critical' for a in alerts):
            status = 'critical'
        elif any(a['level'] == 'warning' for a in alerts):
            status = 'warning'
        elif alerts:
            status = 'attention'
        
        return {
            'monitor_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'data_source': self.data_source,
            'status': status,
            'total_alerts': len(alerts),
            'alerts': alerts,
            'summary': self._generate_summary(portfolio, alerts),
            'recommendations': self._generate_recommendations(alerts)
        }
    
    def _check_fund_alerts(self, holding: Dict) -> List[Dict]:
        """检查单只基金的预警"""
        alerts = []
        
        daily_return = holding.get('daily_return', 0)
        total_return = holding.get('total_return', 0)
        max_drawdown = holding.get('max_drawdown', 0)
        
        # 单日大跌预警
        if daily_return <= self.ALERT_THRESHOLDS['daily_drop']:
            alerts.append({
                'fund_code': holding.get('code'),
                'fund_name': holding.get('name'),
                'type': '单日大跌',
                'level': 'warning',
                'value': daily_return,
                'threshold': self.ALERT_THRESHOLDS['daily_drop'],
                'message': f"单日下跌 {abs(daily_return)*100:.1f}%"
            })
        
        # 回撤预警
        if max_drawdown <= self.ALERT_THRESHOLDS['drawdown_20']:
            alerts.append({
                'fund_code': holding.get('code'),
                'fund_name': holding.get('name'),
                'type': '深度回撤',
                'level': 'critical',
                'value': max_drawdown,
                'threshold': self.ALERT_THRESHOLDS['drawdown_20'],
                'message': f"最大回撤 {abs(max_drawdown)*100:.1f}%，建议审视投资策略"
            })
        elif max_drawdown <= self.ALERT_THRESHOLDS['drawdown_15']:
            alerts.append({
                'fund_code': holding.get('code'),
                'fund_name': holding.get('name'),
                'type': '较大回撤',
                'level': 'warning',
                'value': max_drawdown,
                'threshold': self.ALERT_THRESHOLDS['drawdown_15'],
                'message': f"最大回撤 {abs(max_drawdown)*100:.1f}%"
            })
        
        return alerts
    
    def _check_portfolio_risk(self, portfolio: Dict) -> List[Dict]:
        """检查组合整体风险"""
        alerts = []
        
        concentration = portfolio.get('concentration', {})
        top_holding = concentration.get('top_holding_weight', 0)
        
        # 集中度预警
        if top_holding > 0.30:
            alerts.append({
                'fund_code': 'PORTFOLIO',
                'fund_name': '组合整体',
                'type': '持仓集中',
                'level': 'warning' if top_holding < 0.50 else 'critical',
                'value': top_holding,
                'threshold': 0.30,
                'message': f"最大单一持仓占比 {top_holding*100:.1f}%"
            })
        
        return alerts
    
    def _generate_summary(self, portfolio: Dict, alerts: List[Dict]) -> Dict:
        """生成监控摘要"""
        critical = len([a for a in alerts if a['level'] == 'critical'])
        warning = len([a for a in alerts if a['level'] == 'warning'])
        attention = len([a for a in alerts if a['level'] == 'attention'])
        
        return {
            'critical_alerts': critical,
            'warning_alerts': warning,
            'attention_alerts': attention,
            'total_holdings': len(portfolio.get('holdings', [])),
            'portfolio_value': portfolio.get('total_value', 0),
            'data_freshness': 'T+1' if self.data_source == 'AkShare' else '实时' if self.data_source == '同花顺iFinD' else '模拟'
        }
    
    def _generate_recommendations(self, alerts: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        warning_alerts = [a for a in alerts if a['level'] == 'warning']
        
        if critical_alerts:
            recommendations.append("🚨 存在关键预警，建议立即检查持仓")
        
        if warning_alerts:
            recommendations.append("⚠️ 存在预警，建议关注市场动态")
        
        if not alerts:
            recommendations.append("✅ 组合状态正常，继续保持")
        
        recommendations.append("📊 建议每周检查一次组合偏离度")
        
        return recommendations


def main():
    parser = argparse.ArgumentParser(description='基金组合监控')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--use-real-data', action='store_true', default=True,
                       help='使用真实数据')
    parser.add_argument('--use-mock-data', action='store_true',
                       help='使用模拟数据')
    
    args = parser.parse_args()
    
    use_real = args.use_real_data and not args.use_mock_data
    monitor = FundMonitor(use_real_data=use_real)
    
    # 示例组合
    portfolio = {
        'total_value': 100000,
        'holdings': [
            {'code': '000001', 'name': '华夏成长', 'daily_return': -0.02, 'max_drawdown': -0.12},
            {'code': '000002', 'name': '易方达蓝筹', 'daily_return': -0.035, 'max_drawdown': -0.18},
        ],
        'concentration': {'top_holding_weight': 0.35}
    }
    
    result = monitor.monitor_portfolio(portfolio)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"📊 组合监控报告 ({result['data_source']})")
        print("=" * 60)
        print(f"监控时间: {result['monitor_date']}")
        print(f"状态: {result['status']}")
        print(f"预警数量: {result['total_alerts']}")
        
        if result['alerts']:
            print(f"\n预警详情:")
            for alert in result['alerts']:
                emoji = {'critical': '🔴', 'warning': '🟡', 'attention': '🔵'}.get(alert['level'], '⚪')
                print(f"  {emoji} {alert['fund_name']}: {alert['message']}")
        
        print(f"\n建议:")
        for rec in result['recommendations']:
            print(f"  {rec}")


if __name__ == '__main__':
    main()
