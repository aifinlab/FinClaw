#!/usr/bin/env python3
"""
基金定投规划核心模块
Fund SIP Planner Core Module

功能：定投计划、智能定投、定投回测、止盈止损
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-sip-planner/scripts')

import json
import argparse
import math
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class SIPPlan:
    """定投计划"""
    plan_id: str
    target_amount: float
    monthly_amount: float
    years: int
    strategy: str
    total_periods: int
    expected_return: float
    projected_value: float
    projected_profit: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SIPPlanner:
    """定投规划器"""
    
    # 策略参数
    STRATEGY_PARAMS = {
        'fixed': {'name': '固定定投', 'description': '每期固定金额'},
        'ma': {'name': '均线定投', 'description': '基于均线偏离度调整'},
        'valuation': {'name': '估值定投', 'description': '基于估值分位数调整'},
        'trend': {'name': '趋势定投', 'description': '基于趋势方向调整'},
    }
    
    def __init__(self):
        pass
    
    def create_plan(self, target_amount: float, monthly_amount: float,
                   years: int, strategy: str = 'fixed',
                   expected_return: float = 0.08) -> Dict:
        """
        创建定投计划
        
        Args:
            target_amount: 目标金额
            monthly_amount: 每月定投金额
            years: 投资年限
            strategy: 定投策略
            expected_return: 预期年化收益率
        
        Returns:
            定投计划报告
        """
        total_periods = years * 12
        total_investment = monthly_amount * total_periods
        
        # 计算复利终值
        monthly_rate = (1 + expected_return) ** (1/12) - 1
        projected_value = monthly_amount * ((1 + monthly_rate) ** total_periods - 1) / monthly_rate
        projected_profit = projected_value - total_investment
        
        # 计算达成目标所需时间
        if target_amount > 0:
            periods_to_target = math.log(1 + target_amount * monthly_rate / monthly_amount) / math.log(1 + monthly_rate)
            months_to_target = int(periods_to_target)
            target_date = datetime.now() + timedelta(days=30*months_to_target)
        else:
            months_to_target = total_periods
            target_date = datetime.now() + timedelta(days=365*years)
        
        # 生成定投日历
        schedule = []
        start_date = datetime.now()
        for i in range(min(12, total_periods)):  # 只显示前12期
            period_date = start_date + timedelta(days=30*i)
            cumulative = monthly_amount * (i + 1)
            projected = monthly_amount * ((1 + monthly_rate) ** (i + 1) - 1) / monthly_rate
            schedule.append({
                'period': i + 1,
                'date': period_date.strftime('%Y-%m-%d'),
                'amount': monthly_amount,
                'cumulative_investment': cumulative,
                'projected_value': round(projected, 2)
            })
        
        strategy_info = self.STRATEGY_PARAMS.get(strategy, self.STRATEGY_PARAMS['fixed'])
        
        return {
            'plan_id': f'SIP_{datetime.now().strftime("%Y%m%d")}_{strategy}',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'target_amount': target_amount,
            'monthly_amount': monthly_amount,
            'years': years,
            'total_periods': total_periods,
            'strategy': strategy,
            'strategy_name': strategy_info['name'],
            'strategy_description': strategy_info['description'],
            'expected_return': expected_return,
            'projections': {
                'total_investment': total_investment,
                'projected_value': round(projected_value, 2),
                'projected_profit': round(projected_profit, 2),
                'return_rate': round(projected_profit / total_investment * 100, 2),
                'annualized_return': expected_return * 100
            },
            'target_analysis': {
                'months_to_target': months_to_target,
                'target_date': target_date.strftime('%Y-%m-%d'),
                'can_reach_target': projected_value >= target_amount
            },
            'payment_schedule': schedule,
            'recommendations': self._generate_recommendations(strategy)
        }
    
    def backtest(self, fund_code: str, strategy: str = 'fixed',
                base_amount: float = 1000, years: int = 3) -> Dict:
        """
        定投回测
        
        Args:
            fund_code: 基金代码
            strategy: 定投策略
            base_amount: 基础定投金额
            years: 回测年限
        
        Returns:
            回测报告
        """
        # 模拟回测数据
        periods = years * 12
        
        # 模拟净值数据 (带波动)
        navs = self._generate_nav_series(periods)
        
        # 固定定投回测
        fixed_result = self._backtest_fixed(navs, base_amount)
        
        # 智能定投回测
        if strategy == 'ma':
            smart_result = self._backtest_ma(navs, base_amount)
        elif strategy == 'valuation':
            smart_result = self._backtest_valuation(navs, base_amount)
        elif strategy == 'trend':
            smart_result = self._backtest_trend(navs, base_amount)
        else:
            smart_result = fixed_result
        
        return {
            'fund_code': fund_code,
            'backtest_period': f'{years}年 ({periods}期)',
            'start_date': (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'strategy': strategy,
            'comparison': {
                'fixed': fixed_result,
                'smart': smart_result
            },
            'analysis': self._analyze_backtest(fixed_result, smart_result, strategy)
        }
    
    def _generate_nav_series(self, periods: int) -> List[float]:
        """生成模拟净值序列"""
        navs = [1.0]
        for _ in range(periods):
            # 模拟月收益率 (-5% ~ +8%)
            change = 0.005 + (hash(str(_)) % 1000 / 100000 - 0.005) * 10
            navs.append(navs[-1] * (1 + change))
        return navs
    
    def _backtest_fixed(self, navs: List[float], amount: float) -> Dict:
        """固定定投回测"""
        total_invested = 0.0
        total_shares = 0.0
        
        for i, nav in enumerate(navs[1:], 1):
            total_invested += amount
            total_shares += amount / nav
        
        final_value = total_shares * navs[-1]
        profit = final_value - total_invested
        return_rate = profit / total_invested if total_invested > 0 else 0
        avg_cost = total_invested / total_shares if total_shares > 0 else 0
        
        # 计算年化收益
        years = len(navs) / 12
        annualized = (final_value / total_invested) ** (1/years) - 1 if years > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'final_value': round(final_value, 2),
            'profit': round(profit, 2),
            'return_rate': round(return_rate * 100, 2),
            'annualized_return': round(annualized * 100, 2),
            'avg_cost': round(avg_cost, 4),
            'total_shares': round(total_shares, 4)
        }
    
    def _backtest_ma(self, navs: List[float], base_amount: float) -> Dict:
        """均线定投回测"""
        ma_window = 6  # 6月均线
        total_invested = 0.0
        total_shares = 0.0
        
        for i, nav in enumerate(navs[1:], 1):
            if i >= ma_window:
                ma = sum(navs[i-ma_window:i]) / ma_window
                deviation = (nav - ma) / ma
            else:
                deviation = 0
            
            # 调整系数
            if deviation < -0.20:
                multiplier = 2.0
            elif deviation < -0.10:
                multiplier = 1.5
            elif deviation < 0.10:
                multiplier = 1.0
            elif deviation < 0.20:
                multiplier = 0.8
            else:
                multiplier = 0.5
            
            amount = base_amount * multiplier
            total_invested += amount
            total_shares += amount / nav
        
        final_value = total_shares * navs[-1]
        profit = final_value - total_invested
        return_rate = profit / total_invested if total_invested > 0 else 0
        avg_cost = total_invested / total_shares if total_shares > 0 else 0
        
        years = len(navs) / 12
        annualized = (final_value / total_invested) ** (1/years) - 1 if years > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'final_value': round(final_value, 2),
            'profit': round(profit, 2),
            'return_rate': round(return_rate * 100, 2),
            'annualized_return': round(annualized * 100, 2),
            'avg_cost': round(avg_cost, 4),
            'total_shares': round(total_shares, 4)
        }
    
    def _backtest_valuation(self, navs: List[float], base_amount: float) -> Dict:
        """估值定投回测"""
        total_invested = 0.0
        total_shares = 0.0
        
        for i, nav in enumerate(navs[1:], 1):
            # 模拟估值分位数 (基于历史位置)
            history = navs[max(0, i-24):i]
            if history:
                sorted_hist = sorted(history)
                rank = sum(1 for h in history if h <= nav)
                percentile = rank / len(history)
            else:
                percentile = 0.5
            
            # 估值调整
            if percentile < 0.30:
                multiplier = 2.0
            elif percentile < 0.70:
                multiplier = 1.0
            else:
                multiplier = 0.5
            
            amount = base_amount * multiplier
            total_invested += amount
            total_shares += amount / nav
        
        final_value = total_shares * navs[-1]
        profit = final_value - total_invested
        return_rate = profit / total_invested if total_invested > 0 else 0
        avg_cost = total_invested / total_shares if total_shares > 0 else 0
        
        years = len(navs) / 12
        annualized = (final_value / total_invested) ** (1/years) - 1 if years > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'final_value': round(final_value, 2),
            'profit': round(profit, 2),
            'return_rate': round(return_rate * 100, 2),
            'annualized_return': round(annualized * 100, 2),
            'avg_cost': round(avg_cost, 4),
            'total_shares': round(total_shares, 4)
        }
    
    def _backtest_trend(self, navs: List[float], base_amount: float) -> Dict:
        """趋势定投回测"""
        total_invested = 0.0
        total_shares = 0.0
        
        for i, nav in enumerate(navs[1:], 1):
            # 简单趋势判断 (3月vs6月均线)
            if i >= 6:
                ma3 = sum(navs[i-3:i]) / 3
                ma6 = sum(navs[i-6:i]) / 6
                
                if ma3 > ma6 * 1.02:
                    trend = 'up'
                    multiplier = 1.0
                elif ma3 < ma6 * 0.98:
                    trend = 'down'
                    multiplier = 1.8
                else:
                    trend = 'neutral'
                    multiplier = 1.2
            else:
                multiplier = 1.0
            
            amount = base_amount * multiplier
            total_invested += amount
            total_shares += amount / nav
        
        final_value = total_shares * navs[-1]
        profit = final_value - total_invested
        return_rate = profit / total_invested if total_invested > 0 else 0
        avg_cost = total_invested / total_shares if total_shares > 0 else 0
        
        years = len(navs) / 12
        annualized = (final_value / total_invested) ** (1/years) - 1 if years > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'final_value': round(final_value, 2),
            'profit': round(profit, 2),
            'return_rate': round(return_rate * 100, 2),
            'annualized_return': round(annualized * 100, 2),
            'avg_cost': round(avg_cost, 4),
            'total_shares': round(total_shares, 4)
        }
    
    def _analyze_backtest(self, fixed: Dict, smart: Dict, strategy: str) -> Dict:
        """分析回测结果"""
        analysis = {
            'key_findings': [],
            'pros_cons': {
                'advantages': [],
                'disadvantages': []
            },
            'suitable_for': []
        }
        
        # 比较结果
        if smart['avg_cost'] < fixed['avg_cost']:
            analysis['key_findings'].append(f'智能定投降低了平均成本 ({smart["avg_cost"]} vs {fixed["avg_cost"]})')
        
        if smart['total_invested'] > fixed['total_invested']:
            analysis['key_findings'].append(f'智能定投增加了总投入 ({smart["total_invested"]} vs {fixed["total_invested"]})')
        
        # 策略优缺点
        if strategy == 'ma':
            analysis['pros_cons']['advantages'] = [
                '自动逢低加仓，摊平成本',
                '无需判断估值，执行简单'
            ]
            analysis['pros_cons']['disadvantages'] = [
                '投入金额不稳定',
                '震荡市可能频繁调整'
            ]
            analysis['suitable_for'] = ['波动较大的权益基金', '震荡市环境']
        elif strategy == 'valuation':
            analysis['pros_cons']['advantages'] = [
                '基于估值投资，更理性',
                '低估值时多投，长期收益好'
            ]
            analysis['pros_cons']['disadvantages'] = [
                '需要准确的估值数据',
                '高估值期可能踏空'
            ]
            analysis['suitable_for'] = ['宽基指数基金', '有明确估值指标的品种']
        
        return analysis
    
    def calculate_profit(self, monthly_amount: float, periods: int,
                        annual_return: float) -> Dict:
        """计算定投收益"""
        monthly_rate = (1 + annual_return) ** (1/12) - 1
        total_invested = monthly_amount * periods
        final_value = monthly_amount * ((1 + monthly_rate) ** periods - 1) / monthly_rate
        profit = final_value - total_invested
        
        return {
            'monthly_amount': monthly_amount,
            'periods': periods,
            'years': periods / 12,
            'total_invested': round(total_invested, 2),
            'final_value': round(final_value, 2),
            'profit': round(profit, 2),
            'return_rate': round(profit / total_invested * 100, 2),
            'annualized_return': round(annual_return * 100, 2)
        }
    
    def _generate_recommendations(self, strategy: str) -> List[str]:
        """生成建议"""
        base = [
            '定投需要长期坚持，建议至少3年以上',
            '设置自动扣款，避免断供影响收益',
            '根据收入变化适时调整定投金额'
        ]
        
        if strategy == 'fixed':
            base.extend([
                '固定定投最简单省心，适合初学者',
                '在市场低位时可考虑手动加投'
            ])
        elif strategy in ['ma', 'valuation', 'trend']:
            base.extend([
                '智能定投可能增加投入金额，需预留资金',
                '建议设置投入金额上下限，避免极端情况'
            ])
        
        base.extend([
            '建议设置15%-20%止盈目标',
            '定投不是万能，极端行情需灵活调整'
        ])
        
        return base


def print_plan_report(report: Dict):
    """打印定投计划报告"""
    print("\n" + "=" * 70)
    print("📊 定投计划报告")
    print("=" * 70)
    
    print(f"\n计划ID: {report['plan_id']}")
    print(f"创建日期: {report['created_at']}")
    print(f"定投策略: {report['strategy_name']}")
    print(f"策略说明: {report['strategy_description']}")
    
    print(f"\n💰 定投参数:")
    print(f"  目标金额: ¥{report['target_amount']:,.0f}")
    print(f"  每月定投: ¥{report['monthly_amount']:,.0f}")
    print(f"  投资年限: {report['years']}年 ({report['total_periods']}期)")
    print(f"  预期年化收益: {report['expected_return']*100:.1f}%")
    
    proj = report['projections']
    print(f"\n📈 预期收益:")
    print(f"  累计投入: ¥{proj['total_investment']:,.0f}")
    print(f"  预期总值: ¥{proj['projected_value']:,.0f}")
    print(f"  预期收益: ¥{proj['projected_profit']:,.0f} ({proj['return_rate']:.1f}%)")
    print(f"  年化收益: {proj['annualized_return']:.1f}%")
    
    target = report['target_analysis']
    print(f"\n🎯 目标分析:")
    if target['can_reach_target']:
        print(f"  ✅ 预计{target['months_to_target']}个月后可达成目标")
        print(f"  📅 预计达成日期: {target['target_date']}")
    else:
        print(f"  ⚠️ 按当前计划可能无法达成目标")
        print(f"  💡 建议: 增加每月定投金额或延长投资期限")
    
    print(f"\n📅 定投日历 (前12期):")
    print(f"{'期数':<6} {'日期':<12} {'金额':<10} {'累计投入':<12} {'预期价值':<12}")
    print("-" * 60)
    for s in report['payment_schedule']:
        print(f"{s['period']:<6} {s['date']:<12} ¥{s['amount']:<8,.0f} "
              f"¥{s['cumulative_investment']:<10,.0f} ¥{s['projected_value']:<10,.0f}")
    
    print(f"\n💡 建议:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print("=" * 70)


def print_backtest_report(report: Dict):
    """打印回测报告"""
    print("\n" + "=" * 70)
    print("📊 定投回测报告")
    print("=" * 70)
    
    print(f"\n基金代码: {report['fund_code']}")
    print(f"回测区间: {report['start_date']} ~ {report['end_date']}")
    print(f"回测时长: {report['backtest_period']}")
    print(f"回测策略: {report['strategy']}")
    
    fixed = report['comparison']['fixed']
    smart = report['comparison']['smart']
    
    print(f"\n📈 回测结果对比:")
    print(f"{'指标':<15} {'固定定投':<12} {'智能定投':<12} {'差异':<12}")
    print("-" * 55)
    print(f"{'累计投入':<15} ¥{fixed['total_invested']:<10,.0f} "
          f"¥{smart['total_invested']:<10,.0f} "
          f"{smart['total_invested']-fixed['total_invested']:+.0f}")
    print(f"{'期末市值':<15} ¥{fixed['final_value']:<10,.0f} "
          f"¥{smart['final_value']:<10,.0f} "
          f"{smart['final_value']-fixed['final_value']:+.0f}")
    print(f"{'总收益':<15} ¥{fixed['profit']:<10,.0f} "
          f"¥{smart['profit']:<10,.0f} "
          f"{smart['profit']-fixed['profit']:+.0f}")
    print(f"{'收益率':<15} {fixed['return_rate']:<10.1f}% "
          f"{smart['return_rate']:<10.1f}% "
          f"{smart['return_rate']-fixed['return_rate']:+.1f}%")
    print(f"{'年化收益':<15} {fixed['annualized_return']:<10.1f}% "
          f"{smart['annualized_return']:<10.1f}% "
          f"{smart['annualized_return']-fixed['annualized_return']:+.1f}%")
    print(f"{'平均成本':<15} {fixed['avg_cost']:<10.4f} "
          f"{smart['avg_cost']:<10.4f} "
          f"{(smart['avg_cost']/fixed['avg_cost']-1)*100:+.1f}%")
    
    analysis = report['analysis']
    print(f"\n🔍 分析结论:")
    for finding in analysis['key_findings']:
        print(f"  • {finding}")
    
    print(f"\n✅ 优势:")
    for adv in analysis['pros_cons']['advantages']:
        print(f"  • {adv}")
    
    print(f"\n⚠️ 劣势:")
    for dis in analysis['pros_cons']['disadvantages']:
        print(f"  • {dis}")
    
    print(f"\n👤 适合人群:")
    for suitable in analysis['suitable_for']:
        print(f"  • {suitable}")
    
    print("=" * 70)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金定投规划')
    parser.add_argument('--target', type=float, required=True, help='目标金额')
    parser.add_argument('--monthly', type=float, default=2000, help='每月定投金额')
    parser.add_argument('--years', type=int, default=5, help='投资年限')
    parser.add_argument('--strategy', default='fixed', 
                       choices=['fixed', 'ma', 'valuation', 'trend'],
                       help='定投策略')
    parser.add_argument('--backtest', action='store_true', help='回测模式')
    parser.add_argument('--fund', default='000001', help='基金代码（回测）')
    parser.add_argument('--amount', type=float, default=1000, help='基础金额（回测）')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    planner = SIPPlanner()
    
    if args.backtest:
        report = planner.backtest(
            fund_code=args.fund,
            strategy=args.strategy,
            base_amount=args.amount,
            years=args.years
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_backtest_report(report)
    else:
        report = planner.create_plan(
            target_amount=args.target,
            monthly_amount=args.monthly,
            years=args.years,
            strategy=args.strategy
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_plan_report(report)


if __name__ == '__main__':
    main()
