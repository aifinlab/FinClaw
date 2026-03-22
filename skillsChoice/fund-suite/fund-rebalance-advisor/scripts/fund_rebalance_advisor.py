#!/usr/bin/env python3
"""
基金换仓建议核心模块
Fund Rebalance Advisor Core Module

功能：偏离度检测、再平衡建议、换仓优化、成本控制
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-rebalance-advisor/scripts')

import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class Holding:
    """持仓"""
    fund_code: str
    fund_name: str
    fund_type: str
    current_value: float
    current_weight: float
    target_weight: float
    holding_days: int
    cost_basis: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RebalanceAdvisor:
    """换仓建议器"""
    
    # 赎回费率表
    REDEMPTION_FEES = {
        (0, 7): 0.015,      # 0-7天: 1.5%
        (7, 30): 0.0075,    # 7-30天: 0.75%
        (30, 365): 0.005,   # 30-365天: 0.5%
        (365, 730): 0.0025, # 1-2年: 0.25%
        (730, float('inf')): 0.0  # >2年: 0%
    }
    
    # 偏离度阈值
    DEVIATION_THRESHOLDS = {
        'green': 0.03,   # 3% - 正常
        'yellow': 0.05,  # 5% - 关注
        'orange': 0.10,  # 10% - 建议再平衡
        'red': 0.20,     # 20% - 强烈建议
    }
    
    def __init__(self):
        pass
    
    def check_deviation(self, portfolio: Dict, target_allocation: Dict) -> Dict:
        """
        检测偏离度
        
        Args:
            portfolio: 当前组合
            target_allocation: 目标配置
        
        Returns:
            偏离度分析报告
        """
        total_value = portfolio.get('total_value', 0)
        holdings = portfolio.get('holdings', [])
        
        deviations = []
        max_deviation = 0
        total_deviation = 0
        
        for holding in holdings:
            fund_type = holding.get('fund_type', 'unknown')
            current_weight = holding.get('value', 0) / total_value if total_value > 0 else 0
            target_weight = target_allocation.get(fund_type, 0)
            
            if target_weight > 0:
                deviation = abs(current_weight - target_weight) / target_weight
            else:
                deviation = current_weight  # 目标为0，当前有持仓
            
            deviation_pct = deviation * 100
            max_deviation = max(max_deviation, deviation)
            total_deviation += deviation
            
            # 确定状态
            if deviation <= self.DEVIATION_THRESHOLDS['green']:
                status = '✅'
                level = 'normal'
            elif deviation <= self.DEVIATION_THRESHOLDS['yellow']:
                status = '✅'
                level = 'minor'
            elif deviation <= self.DEVIATION_THRESHOLDS['orange']:
                status = '🟡'
                level = 'moderate'
            else:
                status = '🔴'
                level = 'severe'
            
            deviations.append({
                'fund_type': fund_type,
                'target_weight': target_weight,
                'current_weight': current_weight,
                'deviation': deviation,
                'deviation_pct': deviation_pct,
                'status': status,
                'level': level
            })
        
        avg_deviation = total_deviation / len(holdings) if holdings else 0
        
        # 是否需要再平衡
        needs_rebalance = max_deviation > self.DEVIATION_THRESHOLDS['yellow']
        urgency = 'low'
        if max_deviation > self.DEVIATION_THRESHOLDS['red']:
            urgency = 'high'
        elif max_deviation > self.DEVIATION_THRESHOLDS['orange']:
            urgency = 'medium'
        
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'total_value': total_value,
            'deviation_analysis': {
                'max_deviation': max_deviation,
                'max_deviation_pct': max_deviation * 100,
                'avg_deviation': avg_deviation,
                'avg_deviation_pct': avg_deviation * 100,
                'needs_rebalance': needs_rebalance,
                'urgency': urgency
            },
            'details': sorted(deviations, key=lambda x: x['deviation'], reverse=True)
        }
    
    def generate_advice(self, portfolio: Dict, target_allocation: Dict,
                       constraints: Optional[Dict] = None) -> Dict:
        """
        生成换仓建议
        
        Args:
            portfolio: 当前组合
            target_allocation: 目标配置
            constraints: 约束条件
        
        Returns:
            换仓建议报告
        """
        constraints = constraints or {}
        total_value = portfolio.get('total_value', 0)
        holdings = portfolio.get('holdings', [])
        
        # 计算每类资产当前权重
        current_weights = {}
        for holding in holdings:
            fund_type = holding.get('fund_type', 'unknown')
            current_weights[fund_type] = current_weights.get(fund_type, 0) + holding.get('value', 0)
        
        for fund_type in current_weights:
            current_weights[fund_type] /= total_value if total_value > 0 else 1
        
        # 计算需要调整的资金
        transactions = []
        total_sell = 0
        total_buy = 0
        
        all_types = set(list(current_weights.keys()) + list(target_allocation.keys()))
        
        for fund_type in all_types:
            current = current_weights.get(fund_type, 0)
            target = target_allocation.get(fund_type, 0)
            diff = target - current
            
            if abs(diff) > 0.01:  # 差异超过1%才处理
                amount = abs(diff) * total_value
                if diff > 0:
                    # 需要买入
                    transactions.append({
                        'type': 'buy',
                        'fund_type': fund_type,
                        'target_weight': target,
                        'current_weight': current,
                        'diff': diff,
                        'amount': amount,
                        'reason': f'underweight {diff*100:.1f}%'
                    })
                    total_buy += amount
                else:
                    # 需要卖出
                    transactions.append({
                        'type': 'sell',
                        'fund_type': fund_type,
                        'target_weight': target,
                        'current_weight': current,
                        'diff': diff,
                        'amount': amount,
                        'reason': f'overweight {abs(diff)*100:.1f}%'
                    })
                    total_sell += amount
        
        # 生成具体交易建议
        detailed_transactions = self._generate_transactions(
            holdings, transactions, total_value
        )
        
        # 计算成本
        costs = self._calculate_costs(detailed_transactions)
        
        # 生成执行计划
        execution_plan = self._generate_execution_plan(
            detailed_transactions, costs, constraints
        )
        
        return {
            'report_id': f'RB_{datetime.now().strftime("%Y%m%d")}_001',
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'current_portfolio': portfolio,
            'target_allocation': target_allocation,
            'rebalance_summary': {
                'total_sell': total_sell,
                'total_buy': total_buy,
                'net_adjustment': abs(total_sell - total_buy)
            },
            'transactions': detailed_transactions,
            'cost_analysis': costs,
            'execution_plan': execution_plan,
            'recommendations': self._generate_recommendations(costs)
        }
    
    def _generate_transactions(self, holdings: List[Dict], 
                              adjustments: List[Dict], total_value: float) -> List[Dict]:
        """生成具体交易建议"""
        transactions = []
        
        for adj in adjustments:
            fund_type = adj['fund_type']
            amount = adj['amount']
            
            if adj['type'] == 'sell':
                # 卖出该类型下的基金
                type_holdings = [h for h in holdings if h.get('fund_type') == fund_type]
                
                # 优先卖出持有期长（费用低）的
                type_holdings.sort(key=lambda x: x.get('holding_days', 0), reverse=True)
                
                remaining_to_sell = amount
                for holding in type_holdings:
                    if remaining_to_sell <= 0:
                        break
                    
                    sell_amount = min(remaining_to_sell, holding.get('value', 0))
                    holding_days = holding.get('holding_days', 0)
                    fee_rate = self._get_redemption_fee(holding_days)
                    fee = sell_amount * fee_rate
                    
                    transactions.append({
                        'type': 'sell',
                        'fund_code': holding.get('fund_code'),
                        'fund_name': holding.get('fund_name'),
                        'amount': sell_amount,
                        'holding_days': holding_days,
                        'fee_rate': fee_rate,
                        'fee': fee,
                        'reason': adj['reason']
                    })
                    
                    remaining_to_sell -= sell_amount
            
            else:  # buy
                # 买入建议（需要用户指定具体基金）
                transactions.append({
                    'type': 'buy',
                    'fund_type': fund_type,
                    'amount': amount,
                    'reason': adj['reason'],
                    'note': '请从该类型基金中选择具体标的'
                })
        
        return transactions
    
    def _get_redemption_fee(self, holding_days: int) -> float:
        """获取赎回费率"""
        for (min_days, max_days), fee in self.REDEMPTION_FEES.items():
            if min_days <= holding_days < max_days:
                return fee
        return 0.0
    
    def _calculate_costs(self, transactions: List[Dict]) -> Dict:
        """计算成本"""
        total_redemption_fee = sum(
            t.get('fee', 0) for t in transactions if t['type'] == 'sell'
        )
        
        total_sell_amount = sum(
            t.get('amount', 0) for t in transactions if t['type'] == 'sell'
        )
        
        # 估算税费 (基金赎回暂免个税)
        estimated_tax = 0
        
        # 总成本
        total_cost = total_redemption_fee + estimated_tax
        
        return {
            'redemption_fees': round(total_redemption_fee, 2),
            'estimated_tax': round(estimated_tax, 2),
            'total_cost': round(total_cost, 2),
            'cost_percentage': round(total_cost / total_sell_amount * 100, 3) if total_sell_amount > 0 else 0
        }
    
    def _generate_execution_plan(self, transactions: List[Dict], costs: Dict,
                                constraints: Dict) -> Dict:
        """生成执行计划"""
        total_cost = costs.get('total_cost', 0)
        cost_threshold = constraints.get('cost_threshold', 500)
        
        # 判断是一次性还是分批
        if total_cost > cost_threshold:
            method = 'batch'
            batches = 2
        else:
            method = 'one_time'
            batches = 1
        
        # 生成时间表
        schedule = []
        today = datetime.now()
        
        if method == 'one_time':
            schedule.append({
                'date': today.strftime('%Y-%m-%d'),
                'actions': transactions
            })
        else:
            # 分批执行
            sell_txns = [t for t in transactions if t['type'] == 'sell']
            buy_txns = [t for t in transactions if t['type'] == 'buy']
            
            # 第一批：先卖出一半
            schedule.append({
                'date': today.strftime('%Y-%m-%d'),
                'actions': sell_txns[:len(sell_txns)//2] + buy_txns[:len(buy_txns)//2],
                'note': '第一批换仓'
            })
            
            # 第二批：一个月后
            next_month = today + timedelta(days=30)
            schedule.append({
                'date': next_month.strftime('%Y-%m-%d'),
                'actions': sell_txns[len(sell_txns)//2:] + buy_txns[len(buy_txns)//2:],
                'note': '第二批换仓'
            })
        
        return {
            'method': method,
            'batches': batches,
            'schedule': schedule,
            'rationale': '成本较低，建议一次性完成' if method == 'one_time' else '成本较高，建议分批执行'
        }
    
    def _generate_recommendations(self, costs: Dict) -> List[str]:
        """生成建议"""
        recs = [
            '再平衡建议在市场相对平稳时执行',
            '避免在市场剧烈波动期间进行大额换仓'
        ]
        
        if costs.get('redemption_fees', 0) > 0:
            recs.append('部分基金持有期较短，赎回费较高，可考虑延迟换仓')
        
        recs.extend([
            '可利用新增资金或分红再投进行自然再平衡',
            '换仓后建议保持至少3个月不再调整',
            '定期检查偏离度，但不要过度交易'
        ])
        
        return recs
    
    def simulate_rebalance(self, portfolio: Dict, transactions: List[Dict]) -> Dict:
        """模拟换仓效果"""
        # 模拟换仓后的组合
        new_holdings = []
        total_value = portfolio.get('total_value', 0)
        
        # 应用卖出
        for txn in transactions:
            if txn['type'] == 'sell':
                total_value -= txn.get('fee', 0)
        
        # 计算新的权重
        # 简化的模拟
        return {
            'simulated_portfolio': {
                'total_value': total_value,
                'note': '模拟换仓后组合'
            },
            'impact': {
                'value_change': -sum(t.get('fee', 0) for t in transactions),
                'cost_ratio': sum(t.get('fee', 0) for t in transactions) / portfolio.get('total_value', 1)
            }
        }


def print_deviation_report(report: Dict):
    """打印偏离度报告"""
    print("\n" + "=" * 70)
    print("📊 偏离度检测报告")
    print("=" * 70)
    
    print(f"\n组合价值: ¥{report['total_value']:,.0f}")
    print(f"检测日期: {report['report_date']}")
    
    analysis = report['deviation_analysis']
    print(f"\n偏离度分析:")
    print(f"  最大偏离度: {analysis['max_deviation_pct']:.1f}%")
    print(f"  平均偏离度: {analysis['avg_deviation_pct']:.1f}%")
    
    urgency_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
    urgency_text = {'low': '正常', 'medium': '建议关注', 'high': '强烈建议再平衡'}
    print(f"  紧急程度: {urgency_emoji.get(analysis['urgency'], '⚪')} {urgency_text.get(analysis['urgency'], '未知')}")
    
    if analysis['needs_rebalance']:
        print(f"  状态: 🔴 建议进行再平衡")
    else:
        print(f"  状态: ✅ 偏离度在合理范围内")
    
    print(f"\n详情:")
    print(f"{'资产类型':<10} {'目标':<8} {'当前':<8} {'偏离':<10} {'状态':<6}")
    print("-" * 50)
    for d in report['details']:
        print(f"{d['fund_type']:<10} {d['target_weight']*100:>6.1f}% {d['current_weight']*100:>6.1f}% "
              f"{d['deviation_pct']:>+7.1f}% {d['status']}")
    
    print("=" * 70)


def print_advice_report(report: Dict):
    """打印建议报告"""
    print("\n" + "=" * 70)
    print("📊 换仓建议报告")
    print("=" * 70)
    
    print(f"\n报告ID: {report['report_id']}")
    print(f"报告日期: {report['report_date']}")
    
    summary = report['rebalance_summary']
    print(f"\n换仓汇总:")
    print(f"  总卖出: ¥{summary['total_sell']:,.0f}")
    print(f"  总买入: ¥{summary['total_buy']:,.0f}")
    print(f"  净调整: ¥{summary['net_adjustment']:,.0f}")
    
    print(f"\n建议交易:")
    print(f"{'类型':<6} {'基金':<15} {'金额':<12} {'费用':<10} {'原因':<15}")
    print("-" * 70)
    for t in report['transactions']:
        if t['type'] == 'sell':
            print(f"{'卖出':<6} {t.get('fund_name', t.get('fund_type', 'N/A'))[:13]:<15} "
                  f"¥{t.get('amount', 0):<10,.0f} ¥{t.get('fee', 0):<8,.0f} ({t.get('fee_rate', 0)*100:.2f}%) "
                  f"{t.get('reason', '')}")
        else:
            print(f"{'买入':<6} {t.get('fund_type', 'N/A'):<15} "
                  f"¥{t.get('amount', 0):<10,.0f} {'-':<10} {t.get('reason', '')}")
    
    costs = report['cost_analysis']
    print(f"\n成本分析:")
    print(f"  赎回费: ¥{costs['redemption_fees']:,.2f}")
    print(f"  预估税费: ¥{costs['estimated_tax']:,.2f}")
    print(f"  总成本: ¥{costs['total_cost']:,.2f} ({costs['cost_percentage']:.3f}%)")
    
    plan = report['execution_plan']
    print(f"\n执行计划:")
    print(f"  方式: {'一次性执行' if plan['method'] == 'one_time' else '分批执行'}")
    print(f"  批次数: {plan['batches']}")
    print(f"  说明: {plan['rationale']}")
    
    for i, batch in enumerate(plan['schedule'], 1):
        print(f"\n  第{i}批 ({batch['date']}):")
        for action in batch['actions']:
            print(f"    {action['type']}: {action.get('fund_name', action.get('fund_type', 'N/A'))} "
                  f"¥{action.get('amount', 0):,.0f}")
    
    print(f"\n💡 建议:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print("=" * 70)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金换仓建议')
    parser.add_argument('--check', action='store_true', help='检测偏离度')
    parser.add_argument('--advise', action='store_true', help='生成建议')
    parser.add_argument('--current', help='当前组合JSON文件')
    parser.add_argument('--target', help='目标配置JSON')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    advisor = RebalanceAdvisor()
    
    # 示例数据
    sample_portfolio = {
        'total_value': 1000000,
        'holdings': [
            {'fund_code': '000003', 'fund_name': '中欧时代先锋', 'fund_type': 'equity', 'value': 200000, 'holding_days': 800, 'cost_basis': 180000},
            {'fund_code': '000009', 'fund_name': '广发科技创新', 'fund_type': 'equity', 'value': 150000, 'holding_days': 400, 'cost_basis': 140000},
            {'fund_code': '000005', 'fund_name': '景顺长城新兴', 'fund_type': 'equity', 'value': 70000, 'holding_days': 900, 'cost_basis': 65000},
            {'fund_code': '000001', 'fund_name': '华夏成长混合', 'fund_type': 'hybrid', 'value': 180000, 'holding_days': 1000, 'cost_basis': 160000},
            {'fund_code': '000002', 'fund_name': '易方达蓝筹精选', 'fund_type': 'hybrid', 'value': 100000, 'holding_days': 600, 'cost_basis': 95000},
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
    
    if args.check:
        report = advisor.check_deviation(sample_portfolio, target_allocation)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_deviation_report(report)
    
    elif args.advise:
        report = advisor.generate_advice(sample_portfolio, target_allocation)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_advice_report(report)
    
    else:
        # 默认检测偏离度
        report = advisor.check_deviation(sample_portfolio, target_allocation)
        print_deviation_report(report)


if __name__ == '__main__':
    main()
