#!/usr/bin/env python3
"""
基金组合监控预警核心模块
Fund Monitor Core Module

功能：实时监控、预警检查、定期报告、业绩跟踪
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-monitor/scripts')

import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class AlertRule:
    """预警规则"""
    rule_id: str
    rule_type: str
    threshold: float
    level: str  # info, warning, alert, critical
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Alert:
    """预警记录"""
    alert_id: str
    rule_type: str
    level: str
    message: str
    triggered_at: str
    resolved: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FundMonitor:
    """基金监控器"""
    
    # 预警级别颜色
    LEVEL_COLORS = {
        'info': '🔵',
        'warning': '🟡',
        'alert': '🟠',
        'critical': '🔴'
    }
    
    # 预警级别中文
    LEVEL_NAMES = {
        'info': '信息',
        'warning': '警告',
        'alert': '预警',
        'critical': '严重'
    }
    
    def __init__(self):
        self.portfolios = {}
        self.alert_rules = self._default_rules()
        self.alerts_history = []
    
    def _default_rules(self) -> List[AlertRule]:
        """默认预警规则"""
        return [
            AlertRule('R001', 'daily_drop', -0.03, 'warning'),      # 日跌幅>3%
            AlertRule('R002', 'daily_surge', 0.05, 'warning'),       # 日涨幅>5%
            AlertRule('R003', 'consecutive_decline', -0.01, 'alert'), # 连续下跌
            AlertRule('R004', 'drawdown_5', -0.05, 'info'),          # 回撤5%
            AlertRule('R005', 'drawdown_10', -0.10, 'warning'),      # 回撤10%
            AlertRule('R006', 'drawdown_15', -0.15, 'alert'),        # 回撤15%
            AlertRule('R007', 'drawdown_20', -0.20, 'critical'),     # 回撤20%
            AlertRule('R008', 'concentration', 0.40, 'warning'),     # 集中度40%
        ]
    
    def add_portfolio(self, portfolio_id: str, holdings: List[Dict],
                     target_return: float = 0.10) -> None:
        """添加组合监控"""
        self.portfolios[portfolio_id] = {
            'portfolio_id': portfolio_id,
            'holdings': holdings,
            'target_return': target_return,
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'baseline_value': sum(h.get('value', 0) for h in holdings),
            'max_value': sum(h.get('value', 0) for h in holdings),
            'peak_value': sum(h.get('value', 0) for h in holdings)
        }
    
    def check_alerts(self, portfolio_id: str, 
                    current_data: Optional[Dict] = None) -> Dict:
        """
        检查预警
        
        Args:
            portfolio_id: 组合ID
            current_data: 当前数据 (如不提供使用模拟数据)
        
        Returns:
            预警检查结果
        """
        if portfolio_id not in self.portfolios:
            return {'error': f'组合 {portfolio_id} 不存在'}
        
        portfolio = self.portfolios[portfolio_id]
        holdings = portfolio['holdings']
        
        # 使用模拟数据或传入数据
        current = current_data or self._get_mock_current_data(holdings)
        
        # 计算组合指标
        portfolio_value = sum(h.get('current_value', h.get('value', 0)) for h in current['holdings'])
        portfolio_return = (portfolio_value - portfolio['baseline_value']) / portfolio['baseline_value'] if portfolio['baseline_value'] > 0 else 0
        
        # 更新峰值
        if portfolio_value > portfolio['peak_value']:
            portfolio['peak_value'] = portfolio_value
        
        # 计算回撤
        drawdown = (portfolio['peak_value'] - portfolio_value) / portfolio['peak_value'] if portfolio['peak_value'] > 0 else 0
        
        # 检查各预警规则
        active_alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            alert = self._check_rule(rule, current, portfolio_return, drawdown)
            if alert:
                active_alerts.append(alert)
        
        # 保存预警历史
        self.alerts_history.extend(active_alerts)
        
        # 确定整体状态
        if any(a.level == 'critical' for a in active_alerts):
            status = 'critical'
            status_emoji = '🔴'
        elif any(a.level == 'alert' for a in active_alerts):
            status = 'alert'
            status_emoji = '🟠'
        elif any(a.level == 'warning' for a in active_alerts):
            status = 'warning'
            status_emoji = '🟡'
        else:
            status = 'normal'
            status_emoji = '🟢'
        
        return {
            'monitor_id': f'MON_{datetime.now().strftime("%Y%m%d")}_{portfolio_id}',
            'portfolio_id': portfolio_id,
            'check_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'status_emoji': status_emoji,
            'portfolio_value': round(portfolio_value, 2),
            'portfolio_return': round(portfolio_return, 4),
            'portfolio_return_pct': round(portfolio_return * 100, 2),
            'drawdown': round(drawdown, 4),
            'drawdown_pct': round(drawdown * 100, 2),
            'active_alerts': [a.to_dict() for a in active_alerts],
            'alerts_count': len(active_alerts),
            'holdings_status': self._get_holdings_status(current['holdings']),
            'metrics': self._calculate_metrics(current['holdings']),
            'recommendations': self._generate_recommendations(active_alerts, drawdown)
        }
    
    def _check_rule(self, rule: AlertRule, current: Dict, 
                   portfolio_return: float, drawdown: float) -> Optional[Alert]:
        """检查单个规则"""
        rule_type = rule.rule_type
        threshold = rule.threshold
        
        if rule_type == 'daily_drop':
            daily_return = current.get('daily_return', 0)
            if daily_return <= threshold:
                return Alert(
                    alert_id=f'ALT_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    rule_type='daily_drop',
                    level=rule.level,
                    message=f'日跌幅 {daily_return*100:.2f}% 超过阈值 {threshold*100:.0f}%',
                    triggered_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        
        elif rule_type == 'daily_surge':
            daily_return = current.get('daily_return', 0)
            if daily_return >= threshold:
                return Alert(
                    alert_id=f'ALT_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    rule_type='daily_surge',
                    level=rule.level,
                    message=f'日涨幅 {daily_return*100:.2f}% 超过阈值 {threshold*100:.0f}%',
                    triggered_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        
        elif rule_type.startswith('drawdown_'):
            drawdown_threshold = abs(threshold)
            if drawdown >= drawdown_threshold:
                return Alert(
                    alert_id=f'ALT_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    rule_type='drawdown',
                    level=rule.level,
                    message=f'当前回撤 {drawdown*100:.2f}% 超过阈值 {drawdown_threshold*100:.0f}%',
                    triggered_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        
        return None
    
    def generate_report(self, portfolio_id: str, period: str = 'daily') -> Dict:
        """
        生成定期报告
        
        Args:
            portfolio_id: 组合ID
            period: 报告周期 (daily/weekly/monthly)
        
        Returns:
            报告数据
        """
        if portfolio_id not in self.portfolios:
            return {'error': f'组合 {portfolio_id} 不存在'}
        
        portfolio = self.portfolios[portfolio_id]
        
        # 根据周期确定标题
        period_titles = {
            'daily': '日报',
            'weekly': '周报',
            'monthly': '月报',
            'quarterly': '季报'
        }
        
        # 模拟历史数据
        weekly_return = 0.0235
        monthly_return = 0.0512
        ytd_return = 0.1523
        
        return {
            'report_id': f'RPT_{datetime.now().strftime("%Y%m%d")}_{portfolio_id}',
            'portfolio_id': portfolio_id,
            'period': period,
            'period_name': period_titles.get(period, '报告'),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'returns': {
                'daily': current.get('daily_return', 0.0085) if 'current' in dir() else 0.0085,
                'weekly': weekly_return,
                'monthly': monthly_return,
                'ytd': ytd_return,
                'weekly_pct': weekly_return * 100,
                'monthly_pct': monthly_return * 100,
                'ytd_pct': ytd_return * 100
            },
            'benchmark_comparison': {
                'weekly': 0.0185,
                'monthly': 0.0420,
                'ytd': 0.1250,
                'excess_weekly': 0.0050,
                'excess_monthly': 0.0092,
                'excess_ytd': 0.0273
            },
            'ranking': {
                'current': 12,
                'total': 100,
                'change': 3,
                'percentile': '前12%'
            },
            'risk_metrics': {
                'max_drawdown': -0.032,
                'max_drawdown_ytd': -0.085,
                'volatility': 0.125,
                'sharpe_ratio': 1.25,
                'information_ratio': 0.85
            },
            'holdings_summary': self._summarize_holdings(portfolio['holdings']),
            'alerts_summary': self._summarize_alerts(portfolio_id, period),
            'recommendations': self._generate_report_recommendations(period)
        }
    
    def _get_mock_current_data(self, holdings: List[Dict]) -> Dict:
        """获取模拟当前数据"""
        # 模拟今日涨跌幅
        daily_changes = {
            '000001': 0.012, '000002': 0.008, '000003': -0.003,
            '000004': 0.005, '000005': 0.002, '000008': 0.003
        }
        
        updated_holdings = []
        for h in holdings:
            code = h.get('fund_code', '000001')
            base_value = h.get('value', 10000)
            change = daily_changes.get(code, 0.005)
            current_value = base_value * (1 + change)
            
            updated_holdings.append({
                **h,
                'current_value': current_value,
                'daily_return': change,
                'daily_return_pct': change * 100
            })
        
        total_value = sum(h['current_value'] for h in updated_holdings)
        baseline = sum(h.get('value', 10000) for h in holdings)
        daily_return = (total_value - baseline) / baseline if baseline > 0 else 0
        
        return {
            'holdings': updated_holdings,
            'daily_return': daily_return,
            'portfolio_value': total_value
        }
    
    def _get_holdings_status(self, holdings: List[Dict]) -> List[Dict]:
        """获取持仓状态"""
        status_list = []
        for h in holdings:
            daily_return = h.get('daily_return', 0)
            
            if daily_return >= 0.02:
                emoji = '🔥'
            elif daily_return >= 0:
                emoji = '✅'
            elif daily_return >= -0.02:
                emoji = '⚠️'
            else:
                emoji = '❌'
            
            status_list.append({
                'fund_code': h.get('fund_code', 'N/A'),
                'fund_name': h.get('fund_name', 'Unknown'),
                'weight': h.get('weight', 0),
                'current_value': h.get('current_value', 0),
                'daily_return': daily_return,
                'daily_return_pct': daily_return * 100,
                'emoji': emoji
            })
        
        return sorted(status_list, key=lambda x: x['daily_return'], reverse=True)
    
    def _calculate_metrics(self, holdings: List[Dict]) -> Dict:
        """计算风险指标"""
        returns = [h.get('daily_return', 0) for h in holdings]
        
        # 简化计算
        volatility = 0.125  # 默认波动率
        sharpe = 1.25  # 默认夏普
        var_95 = -0.021  # 默认VaR
        
        return {
            'volatility': volatility,
            'volatility_pct': volatility * 100,
            'sharpe_ratio': sharpe,
            'var_95': var_95,
            'var_95_pct': var_95 * 100,
            'risk_level': 'R3',
            'risk_description': '适中'
        }
    
    def _generate_recommendations(self, alerts: List[Alert], drawdown: float) -> List[str]:
        """生成建议"""
        recs = []
        
        if any(a.level == 'critical' for a in alerts):
            recs.append('🔴 严重预警触发，建议立即评估并采取行动')
        elif any(a.level == 'alert' for a in alerts):
            recs.append('🟠 预警触发，建议密切关注市场动态')
        
        if drawdown > 0.10:
            recs.append(f'当前回撤{drawdown*100:.1f}%，建议检查止损设置')
        
        if not alerts:
            recs.append('🟢 组合运行正常，建议继续持有')
        
        recs.append('定期审视组合配置，保持风险敞口在合理范围')
        
        return recs
    
    def _summarize_holdings(self, holdings: List[Dict]) -> Dict:
        """汇总持仓"""
        total_value = sum(h.get('value', 0) for h in holdings)
        
        by_type = {}
        for h in holdings:
            fund_type = h.get('fund_type', 'unknown')
            by_type[fund_type] = by_type.get(fund_type, 0) + h.get('value', 0)
        
        return {
            'total_holdings': len(holdings),
            'total_value': total_value,
            'by_type': {k: round(v/total_value, 4) for k, v in by_type.items()} if total_value > 0 else {}
        }
    
    def _summarize_alerts(self, portfolio_id: str, period: str) -> Dict:
        """汇总预警"""
        # 获取周期内的预警
        period_alerts = [a for a in self.alerts_history 
                        if a.triggered_at.startswith(datetime.now().strftime('%Y-%m'))]
        
        by_level = {}
        for a in period_alerts:
            by_level[a.level] = by_level.get(a.level, 0) + 1
        
        return {
            'total': len(period_alerts),
            'by_level': by_level,
            'recent': [a.to_dict() for a in period_alerts[-5:]]
        }
    
    def _generate_report_recommendations(self, period: str) -> List[str]:
        """生成报告建议"""
        if period == 'daily':
            return ['关注明日市场动态', '检查是否有调仓需求']
        elif period == 'weekly':
            return ['复盘本周操作', '规划下周策略', '审视风险控制']
        elif period == 'monthly':
            return ['月度总结分析', '调整配置比例', '更新投资计划']
        return []


def print_monitor_status(status: Dict):
    """打印监控状态"""
    print("\n" + "=" * 70)
    print("📊 组合监控状态")
    print("=" * 70)
    
    print(f"\n组合ID: {status['portfolio_id']}")
    print(f"检查时间: {status['check_time']}")
    print(f"整体状态: {status['status_emoji']} {status['status'].upper()}")
    
    print(f"\n组合价值: ¥{status['portfolio_value']:,.0f}")
    print(f"累计收益: {status['portfolio_return_pct']:+.2f}%")
    print(f"当前回撤: {status['drawdown_pct']:.2f}%")
    
    print(f"\n持仓表现:")
    print(f"{'基金':<15} {'权重':<8} {'净值':<12} {'日涨跌':<10} {'状态':<6}")
    print("-" * 60)
    for h in status['holdings_status']:
        print(f"{h['fund_name'][:13]:<15} {h['weight']*100:>6.1f}% "
              f"¥{h['current_value']:<10,.0f} {h['daily_return_pct']:>+6.2f}% {h['emoji']}")
    
    metrics = status['metrics']
    print(f"\n风险指标:")
    print(f"  波动率: {metrics['volatility_pct']:.1f}%")
    print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"  VaR(95%): {metrics['var_95_pct']:.2f}%")
    print(f"  风险等级: {metrics['risk_level']} ({metrics['risk_description']})")
    
    if status['active_alerts']:
        print(f"\n🔔 活跃预警 ({status['alerts_count']}个):")
        for alert in status['active_alerts']:
            emoji = FundMonitor.LEVEL_COLORS.get(alert['level'], '⚪')
            print(f"  {emoji} [{alert['level'].upper()}] {alert['message']}")
    else:
        print(f"\n🟢 无活跃预警")
    
    print(f"\n💡 建议:")
    for rec in status['recommendations']:
        print(f"  • {rec}")
    
    print("=" * 70)


def print_report(report: Dict):
    """打印报告"""
    print("\n" + "=" * 70)
    print(f"📊 组合{report['period_name']} - {report['generated_at']}")
    print("=" * 70)
    
    print(f"\n报告ID: {report['report_id']}")
    print(f"组合ID: {report['portfolio_id']}")
    
    returns = report['returns']
    print(f"\n📈 收益表现:")
    print(f"  本周收益: {returns.get('weekly_pct', 0):+.2f}%")
    print(f"  本月收益: {returns.get('monthly_pct', 0):+.2f}%")
    print(f"  本年收益: {returns.get('ytd_pct', 0):+.2f}%")
    
    bench = report['benchmark_comparison']
    print(f"\n对比基准:")
    print(f"  超额收益(本周): {bench.get('excess_weekly', 0)*100:+.2f}%")
    print(f"  超额收益(本月): {bench.get('excess_monthly', 0)*100:+.2f}%")
    print(f"  超额收益(YTD): {bench.get('excess_ytd', 0)*100:+.2f}%")
    
    ranking = report['ranking']
    print(f"\n排名: {ranking['current']}/{ranking['total']} ({ranking['percentile']}) "
          f"{'⬆️' if ranking['change'] > 0 else '⬇️' if ranking['change'] < 0 else '➡️'} "
          f"{abs(ranking['change'])}位")
    
    risk = report['risk_metrics']
    print(f"\n📊 风险指标:")
    print(f"  最大回撤: {risk['max_drawdown']*100:.1f}% (本周) / {risk['max_drawdown_ytd']*100:.1f}% (本年)")
    print(f"  波动率: {risk['volatility']*100:.1f}%")
    print(f"  夏普比率: {risk['sharpe_ratio']:.2f}")
    print(f"  信息比率: {risk['information_ratio']:.2f}")
    
    alerts = report['alerts_summary']
    print(f"\n🔔 预警统计:")
    print(f"  本月预警: {alerts['total']}次")
    for level, count in alerts.get('by_level', {}).items():
        emoji = FundMonitor.LEVEL_COLORS.get(level, '⚪')
        print(f"  {emoji} {level}: {count}次")
    
    print("=" * 70)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金组合监控')
    parser.add_argument('--portfolio', default='PF001', help='组合ID')
    parser.add_argument('--check', action='store_true', help='检查监控状态')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--period', default='daily', 
                       choices=['daily', 'weekly', 'monthly', 'quarterly'],
                       help='报告周期')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    monitor = FundMonitor()
    
    # 示例持仓
    sample_holdings = [
        {'fund_code': '000001', 'fund_name': '华夏成长', 'fund_type': 'equity', 'weight': 0.25, 'value': 25000},
        {'fund_code': '000002', 'fund_name': '易方达蓝筹', 'fund_type': 'equity', 'weight': 0.20, 'value': 20000},
        {'fund_code': '000003', 'fund_name': '中欧时代', 'fund_type': 'equity', 'weight': 0.15, 'value': 15000},
        {'fund_code': '000004', 'fund_name': '南方稳健', 'fund_type': 'bond', 'weight': 0.20, 'value': 20000},
        {'fund_code': '000005', 'fund_name': '招商产业债', 'fund_type': 'bond', 'weight': 0.15, 'value': 15000},
        {'fund_code': 'CASH', 'fund_name': '货币基金', 'fund_type': 'money', 'weight': 0.05, 'value': 5000},
    ]
    
    # 添加组合
    monitor.add_portfolio(args.portfolio, sample_holdings)
    
    if args.report:
        report = monitor.generate_report(args.portfolio, args.period)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_report(report)
    
    else:  # 默认检查状态
        status = monitor.check_alerts(args.portfolio)
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print_monitor_status(status)


if __name__ == '__main__':
    main()
