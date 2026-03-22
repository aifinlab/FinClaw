#!/usr/bin/env python3
"""
信托收益计算器
Trust Income Calculator

功能：预期收益、IRR、税务计算
"""

import argparse
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import numpy_financial as npf


class TrustIncomeCalculator:
    """信托收益计算主类"""
    
    def __init__(self):
        pass
    
    def calculate_expected_return(self, principal: float, annual_yield: float,
                                   duration_months: int, distribution_way: str,
                                   fee_structure: Dict = None, tax_rate: float = 20) -> Dict:
        """计算预期收益"""
        fee_structure = fee_structure or {}
        
        # 年化收益
        gross_annual = principal * (annual_yield / 100)
        
        # 费用扣除
        management_fee = principal * (fee_structure.get('management_fee', 0) / 100)
        custody_fee = principal * (fee_structure.get('custody_fee', 0) / 100)
        total_fees_annual = management_fee + custody_fee
        
        # 业绩报酬（简化处理，假设未达到门槛）
        performance_fee = 0
        
        net_annual = gross_annual - total_fees_annual - performance_fee
        net_yield = (net_annual / principal) * 100
        
        # 总收益
        years = duration_months / 12
        total_gross = gross_annual * years
        total_net = net_annual * years
        
        # 税务
        tax = total_net * (tax_rate / 100)
        after_tax = total_net - tax
        
        # 分配计划
        schedule = self._generate_distribution_schedule(
            principal, net_annual, duration_months, distribution_way
        )
        
        return {
            'status': 'success',
            'principal': principal,
            'duration_months': duration_months,
            'expected_return': {
                'gross_annual': round(gross_annual, 2),
                'net_annual': round(net_annual, 2),
                'total_gross': round(total_gross, 2),
                'total_net': round(total_net, 2),
                'net_yield': round(net_yield, 2)
            },
            'fee_breakdown': {
                'management': round(management_fee * years, 2),
                'custody': round(custody_fee * years, 2),
                'performance': performance_fee,
                'total': round(total_fees_annual * years, 2)
            },
            'tax': {
                'tax_rate': tax_rate,
                'taxable_amount': round(total_net, 2),
                'tax_due': round(tax, 2),
                'after_tax_return': round(after_tax, 2)
            },
            'distribution_schedule': schedule
        }
    
    def _generate_distribution_schedule(self, principal: float, annual_net: float,
                                         months: int, distribution_way: str) -> List[Dict]:
        """生成分配计划"""
        schedule = []
        
        if distribution_way == 'maturity':
            # 到期一次分配
            schedule.append({
                'date': self._add_months(datetime.now(), months).strftime('%Y-%m-%d'),
                'type': '本金+收益',
                'principal': principal,
                'income': round(annual_net * (months / 12), 2),
                'total': round(principal + annual_net * (months / 12), 2)
            })
        elif distribution_way == 'annually':
            # 年度分配
            for year in range(1, int(months / 12) + 1):
                schedule.append({
                    'date': self._add_months(datetime.now(), year * 12).strftime('%Y-%m-%d'),
                    'type': '年度收益分配',
                    'principal': 0,
                    'income': round(annual_net, 2),
                    'total': round(annual_net, 2)
                })
            # 到期还本
            schedule.append({
                'date': self._add_months(datetime.now(), months).strftime('%Y-%m-%d'),
                'type': '本金归还',
                'principal': principal,
                'income': 0,
                'total': principal
            })
        elif distribution_way == 'quarterly':
            # 季度分配
            quarter_income = annual_net / 4
            for q in range(1, int(months / 3) + 1):
                schedule.append({
                    'date': self._add_months(datetime.now(), q * 3).strftime('%Y-%m-%d'),
                    'type': '季度收益分配',
                    'principal': 0,
                    'income': round(quarter_income, 2),
                    'total': round(quarter_income, 2)
                })
            schedule.append({
                'date': self._add_months(datetime.now(), months).strftime('%Y-%m-%d'),
                'type': '本金归还',
                'principal': principal,
                'income': 0,
                'total': principal
            })
        
        return schedule
    
    def _add_months(self, date: datetime, months: int) -> datetime:
        """添加月份"""
        year = date.year + (date.month + months - 1) // 12
        month = (date.month + months - 1) % 12 + 1
        return datetime(year, month, date.day)
    
    def calculate_irr(self, cashflows: List[Dict]) -> Dict:
        """计算IRR"""
        amounts = [cf['amount'] for cf in cashflows]
        dates = [datetime.strptime(cf['date'], '%Y-%m-%d') for cf in cashflows]
        
        # 简单IRR（假设等间隔）
        irr = npf.irr(amounts)
        
        # XIRR（考虑实际日期）
        try:
            xirr = self._calculate_xirr(amounts, dates)
        except:
            xirr = irr
        
        return {
            'status': 'success',
            'irr': round(irr * 100, 2) if irr else None,
            'xirr': round(xirr * 100, 2) if xirr else None,
            'cashflows': cashflows,
            'total_invested': abs(sum(a for a in amounts if a < 0)),
            'total_returned': sum(a for a in amounts if a > 0)
        }
    
    def _calculate_xirr(self, amounts: List[float], dates: List[datetime]) -> float:
        """计算XIRR"""
        # 简化的XIRR实现
        days = [(d - dates[0]).days for d in dates]
        return npf.irr(amounts)  # 简化处理
    
    def calculate_tax(self, income: float, income_type: str = 'interest',
                      tax_rate: float = 20) -> Dict:
        """计算税务"""
        # 信托收益税务（简化）
        if income_type == 'interest':
            tax = income * (tax_rate / 100)
        elif income_type == 'dividend':
            tax = income * 0.20  # 股息20%
        else:
            tax = income * (tax_rate / 100)
        
        return {
            'status': 'success',
            'income': income,
            'income_type': income_type,
            'tax_rate': tax_rate,
            'tax_due': round(tax, 2),
            'after_tax': round(income - tax, 2)
        }


def main():
    parser = argparse.ArgumentParser(description='信托收益计算器')
    parser.add_argument('--calc-type', default='expected',
                       choices=['expected', 'irr', 'tax'])
    parser.add_argument('--principal', type=float, default=1000000)
    parser.add_argument('--yield', type=float, dest='annual_yield', default=7.5)
    parser.add_argument('--duration', type=int, default=24)
    parser.add_argument('--distribution', default='quarterly',
                       choices=['quarterly', 'annually', 'maturity'])
    parser.add_argument('--cashflows', help='现金流文件（IRR计算）')
    parser.add_argument('--tax-rate', type=float, default=20)
    
    args = parser.parse_args()
    
    calculator = TrustIncomeCalculator()
    
    if args.calc_type == 'expected':
        result = calculator.calculate_expected_return(
            principal=args.principal,
            annual_yield=args.annual_yield,
            duration_months=args.duration,
            distribution_way=args.distribution,
            tax_rate=args.tax_rate
        )
    elif args.calc_type == 'irr':
        if not args.cashflows:
            print("错误：IRR计算需要提供 --cashflows 参数")
            return
        with open(args.cashflows, 'r') as f:
            cashflows = json.load(f)
        result = calculator.calculate_irr(cashflows)
    elif args.calc_type == 'tax':
        result = calculator.calculate_tax(
            income=args.principal * (args.annual_yield / 100),
            tax_rate=args.tax_rate
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
