#!/usr/bin/env python3
"""
信托收益计算器 - 接入数据适配器 v2.0
功能：预期收益、IRR、税务计算，支持从数据源获取产品自动计算
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider


def calculate_irr(cash_flows, guess=0.1, max_iter=100, tol=1e-6):
    """计算IRR（内部收益率）- 简化版牛顿迭代法"""
    if not cash_flows or len(cash_flows) < 2:
        return 0.0
    
    rate = guess
    for _ in range(max_iter):
        npv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
        
        d_npv = sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows) if i > 0)
        
        if abs(d_npv) < 1e-10:
            break
        
        new_rate = rate - npv / d_npv
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    
    return rate


class TrustIncomeCalculator:
    """信托收益计算主类 - 接入数据适配器"""
    
    def __init__(self):
        self.data_provider = get_data_provider()
    
    def calculate_from_data_source(self, product_code: str = None, 
                                    principal: float = None,
                                    **filters) -> dict:
        """
        从数据源获取产品并计算收益
        
        Args:
            product_code: 产品代码（可选）
            principal: 投资本金（可选，默认100万）
            **filters: 筛选条件
        
        Returns:
            收益计算结果，包含数据质量标注
        """
        # 获取产品数据
        products = self.data_provider.get_products(**filters)
        
        if not products:
            return {
                'status': 'error',
                'message': '未找到符合条件的产品',
                'data_source': self.data_provider.get_data_source_info()
            }
        
        # 如果指定了产品代码，查找对应产品
        target_product = None
        if product_code:
            for p in products:
                if p.product_code == product_code:
                    target_product = p
                    break
        
        # 如果没找到指定产品，使用第一个
        if not target_product:
            target_product = products[0]
        
        # 使用默认本金或指定本金
        investment_principal = principal if principal else target_product.min_investment * 10000
        
        # 计算收益
        result = self.calculate_expected_return(
            principal=investment_principal,
            annual_yield=target_product.expected_yield,
            duration_months=target_product.duration,
            distribution_way='quarterly',  # 默认按季分配
            tax_rate=20
        )
        
        # 添加产品信息和数据质量标注
        result['product_info'] = {
            'product_code': target_product.product_code,
            'product_name': target_product.product_name,
            'trust_company': target_product.trust_company,
            'risk_level': target_product.risk_level
        }
        
        if target_product.quality_label:
            result['data_quality'] = target_product.quality_label.to_dict()
        
        return result
    
    def calculate_expected_return(self, principal: float, annual_yield: float,
                                   duration_months: int, distribution_way: str,
                                   fee_structure: dict = None, tax_rate: float = 20) -> dict:
        """计算预期收益"""
        fee_structure = fee_structure or {}
        
        # 年化收益
        gross_annual = principal * (annual_yield / 100)
        
        # 费用扣除
        management_fee = principal * (fee_structure.get('management_fee', 0) / 100)
        custody_fee = principal * (fee_structure.get('custody_fee', 0) / 100)
        total_fees_annual = management_fee + custody_fee
        
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
            'distribution_schedule': schedule,
            'effective_yield': round((after_tax / principal / years) * 100, 2)
        }
    
    def _generate_distribution_schedule(self, principal: float, annual_net: float,
                                         months: int, distribution_way: str) -> list:
        """生成分配计划"""
        schedule = []
        
        if distribution_way == 'maturity':
            schedule.append({
                'date': self._add_months(datetime.now(), months).strftime('%Y-%m-%d'),
                'type': '本金+收益',
                'principal': principal,
                'income': round(annual_net * (months / 12), 2),
                'total': round(principal + annual_net * (months / 12), 2)
            })
        elif distribution_way == 'annually':
            for year in range(1, int(months / 12) + 1):
                schedule.append({
                    'date': self._add_months(datetime.now(), year * 12).strftime('%Y-%m-%d'),
                    'type': '年度收益分配',
                    'principal': 0,
                    'income': round(annual_net, 2),
                    'total': round(annual_net, 2)
                })
            schedule.append({
                'date': self._add_months(datetime.now(), months).strftime('%Y-%m-%d'),
                'type': '本金归还',
                'principal': principal,
                'income': 0,
                'total': principal
            })
        elif distribution_way == 'quarterly':
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
    
    def calculate_irr_detailed(self, cashflows: list) -> dict:
        """计算IRR"""
        amounts = [cf['amount'] for cf in cashflows]
        
        irr = calculate_irr(amounts)
        
        return {
            'status': 'success',
            'irr': round(irr * 100, 2) if irr else None,
            'cashflows': cashflows,
            'total_invested': abs(sum(a for a in amounts if a < 0)),
            'total_returned': sum(a for a in amounts if a > 0)
        }
    
    def calculate_tax(self, income: float, income_type: str = 'interest',
                      tax_rate: float = 20) -> dict:
        """计算税务"""
        if income_type == 'interest':
            tax = income * (tax_rate / 100)
        elif income_type == 'dividend':
            tax = income * 0.20
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
    
    def compare_products(self, **filters) -> dict:
        """对比多个产品的收益"""
        products = self.data_provider.get_products(**filters)
        
        if not products:
            return {
                'status': 'error',
                'message': '未找到符合条件的产品'
            }
        
        comparisons = []
        for p in products[:5]:  # 最多对比5个产品
            principal = p.min_investment * 10000
            result = self.calculate_expected_return(
                principal=principal,
                annual_yield=p.expected_yield,
                duration_months=p.duration,
                distribution_way='quarterly'
            )
            
            comparisons.append({
                'product_code': p.product_code,
                'product_name': p.product_name,
                'trust_company': p.trust_company,
                'expected_yield': p.expected_yield,
                'duration': p.duration,
                'risk_level': p.risk_level,
                'net_return': result['expected_return']['total_net'],
                'after_tax_return': result['tax']['after_tax_return'],
                'effective_yield': result['effective_yield'],
                'data_quality': p.quality_label.to_dict() if p.quality_label else None
            })
        
        # 按税后收益排序
        comparisons.sort(key=lambda x: x['after_tax_return'], reverse=True)
        
        return {
            'status': 'success',
            'comparison_count': len(comparisons),
            'comparisons': comparisons,
            'best_choice': comparisons[0] if comparisons else None
        }


def main():
    parser = argparse.ArgumentParser(description='信托收益计算器 v2.0')
    parser.add_argument('--calc-type', default='expected',
                       choices=['expected', 'from_data_source', 'compare', 'tax'],
                       help='计算类型')
    parser.add_argument('--principal', type=float, default=1000000)
    parser.add_argument('--yield', type=float, dest='annual_yield', default=7.5)
    parser.add_argument('--duration', type=int, default=24)
    parser.add_argument('--distribution', default='quarterly',
                       choices=['quarterly', 'annually', 'maturity'])
    parser.add_argument('--trust-company', help='信托公司筛选')
    parser.add_argument('--min-yield', type=float, help='最低收益率筛选')
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
    elif args.calc_type == 'from_data_source':
        filters = {}
        if args.trust_company:
            filters['trust_company'] = args.trust_company
        if args.min_yield:
            filters['min_yield'] = args.min_yield
        result = calculator.calculate_from_data_source(
            principal=args.principal,
            **filters
        )
    elif args.calc_type == 'compare':
        filters = {}
        if args.trust_company:
            filters['trust_company'] = args.trust_company
        if args.min_yield:
            filters['min_yield'] = args.min_yield
        result = calculator.compare_products(**filters)
    elif args.calc_type == 'tax':
        result = calculator.calculate_tax(
            income=args.principal * (args.annual_yield / 100),
            tax_rate=args.tax_rate
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
