#!/usr/bin/env python3
"""
更新版：信托产品综合分析器（集成数据对接层）
"""

import argparse
import json
import sys
from pathlib import Path

# 添加数据对接层路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))

try:
    from trust_data_adapter import get_data_provider, TrustProductData
    DATA_ADAPTER_AVAILABLE = True
except ImportError:
    DATA_ADAPTER_AVAILABLE = False
    print("警告：数据对接层未找到")

# 原有的导入和代码...
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


class TrustType(Enum):
    """信托类型"""
    COLLECTIVE = "集合信托"
    SINGLE = "单一信托"
    PROPERTY = "财产权信托"


class InvestmentType(Enum):
    """投资类型"""
    FIXED_INCOME = "固定收益类"
    EQUITY = "权益类"
    MIXED = "混合类"
    ALTERNATIVE = "商品及金融衍生品类"


class RiskLevel(Enum):
    """风险等级 R1-R5"""
    R1 = ("R1", "低风险", "谨慎型")
    R2 = ("R2", "中低风险", "稳健型")
    R3 = ("R3", "中等风险", "平衡型")
    R4 = ("R4", "中高风险", "进取型")
    R5 = ("R5", "高风险", "激进型")
    
    def __new__(cls, code, risk_name, investor_type):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.code = code
        obj.risk_name = risk_name
        obj.investor_type = investor_type
        return obj


@dataclass
class TrustProduct:
    """信托产品数据模型"""
    product_code: str
    product_name: str
    issuer: str
    trust_type: str
    investment_type: str
    risk_level: str
    min_investment: Decimal
    duration: int
    expected_yield: Decimal
    distribution_way: str
    scale: Decimal
    establishment_date: Optional[str] = None
    maturity_date: Optional[str] = None
    underlying_assets: List[Dict] = None
    risk_measures: Dict = None
    fees: Dict = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'min_investment': float(self.min_investment),
            'expected_yield': float(self.expected_yield),
            'scale': float(self.scale)
        }
    
    @classmethod
    def from_data_adapter(cls, data: 'TrustProductData') -> 'TrustProduct':
        """从数据适配器模型转换"""
        return cls(
            product_code=data.product_code,
            product_name=data.product_name,
            issuer=data.trust_company,
            trust_type=data.product_type,
            investment_type=data.investment_type,
            risk_level=data.risk_level,
            min_investment=Decimal(str(data.min_investment)),
            duration=data.duration,
            expected_yield=Decimal(str(data.expected_yield)),
            distribution_way='按季付息',
            scale=Decimal(str(data.issue_scale)),
            establishment_date=data.issue_date,
            maturity_date=None,
            underlying_assets=[{'type': data.underlying_type}] if data.underlying_type else [],
            risk_measures={},
            fees={}
        )


class RiskAssessmentEngine:
    """风险评估引擎"""
    
    def __init__(self):
        self.weights = {
            'credit_risk': 0.4,
            'market_risk': 0.3,
            'liquidity_risk': 0.3
        }
    
    def assess_credit_risk(self, product: TrustProduct) -> Dict:
        """信用风险评估"""
        score = 70
        
        if product.underlying_assets:
            for asset in product.underlying_assets:
                if asset.get('credit_rating'):
                    rating = asset['credit_rating']
                    if 'AAA' in rating:
                        score += 10
                    elif 'AA' in rating:
                        score += 5
                    elif 'A' in rating:
                        score += 0
                    else:
                        score -= 10
                
                if asset.get('guarantee'):
                    score += 5
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'level': self._score_to_level(score),
            'factors': ['底层资产质量', '担保措施', '融资主体评级']
        }
    
    def assess_market_risk(self, product: TrustProduct) -> Dict:
        """市场风险评估"""
        score = 80
        
        risk_factors = {
            InvestmentType.FIXED_INCOME.value: 0,
            InvestmentType.MIXED.value: -10,
            InvestmentType.EQUITY.value: -20,
            InvestmentType.ALTERNATIVE.value: -25
        }
        
        score += risk_factors.get(product.investment_type, 0)
        
        if product.duration > 36:
            score -= 10
        elif product.duration > 24:
            score -= 5
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'level': self._score_to_level(score),
            'factors': ['投资类型', '期限结构', '利率敏感度']
        }
    
    def assess_liquidity_risk(self, product: TrustProduct) -> Dict:
        """流动性风险评估"""
        score = 75
        
        if product.duration > 36:
            score -= 20
        elif product.duration > 24:
            score -= 10
        elif product.duration > 12:
            score -= 5
        
        if '开放' in product.distribution_way:
            score += 10
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'level': self._score_to_level(score),
            'factors': ['产品期限', '开放频率', '二级市场流动性']
        }
    
    def calculate_overall_risk(self, product: TrustProduct) -> Dict:
        """计算综合风险评分"""
        credit = self.assess_credit_risk(product)
        market = self.assess_market_risk(product)
        liquidity = self.assess_liquidity_risk(product)
        
        overall_score = (
            credit['score'] * self.weights['credit_risk'] +
            market['score'] * self.weights['market_risk'] +
            liquidity['score'] * self.weights['liquidity_risk']
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_level': self._score_to_level(overall_score),
            'credit_risk': credit,
            'market_risk': market,
            'liquidity_risk': liquidity
        }
    
    def _score_to_level(self, score: float) -> str:
        if score >= 80:
            return "低风险"
        elif score >= 60:
            return "中低风险"
        elif score >= 40:
            return "中等风险"
        elif score >= 20:
            return "中高风险"
        else:
            return "高风险"


class ComplianceChecker:
    """合规检查器"""
    
    def __init__(self):
        self.rules = {
            'nested_limit': 2,
            'min_investment': {
                'collective': 300000,
                'single': 1000000
            },
            'investor_qualification': {
                'R1': ['谨慎型', '稳健型', '平衡型', '进取型', '激进型'],
                'R2': ['稳健型', '平衡型', '进取型', '激进型'],
                'R3': ['平衡型', '进取型', '激进型'],
                'R4': ['进取型', '激进型'],
                'R5': ['激进型']
            }
        }
    
    def check_compliance(self, product: TrustProduct) -> Dict:
        """执行合规检查"""
        issues = []
        
        min_required = self.rules['min_investment'].get(
            'collective' if product.trust_type == TrustType.COLLECTIVE.value else 'single'
        )
        if product.min_investment < min_required:
            issues.append({
                'type': '起投金额不足',
                'severity': 'high',
                'description': f'起投金额{product.min_investment}低于最低要求{min_required}'
            })
        
        nested_level = self._check_nested_level(product)
        if nested_level > self.rules['nested_limit']:
            issues.append({
                'type': '嵌套层数超限',
                'severity': 'high',
                'description': f'嵌套层数{nested_level}超过限制{self.rules["nested_limit"]}'
            })
        
        investment_issues = self._check_investment_restrictions(product)
        issues.extend(investment_issues)
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'nested_level': nested_level
        }
    
    def _check_nested_level(self, product: TrustProduct) -> int:
        """检查嵌套层数"""
        level = 1
        if product.underlying_assets:
            for asset in product.underlying_assets:
                if asset.get('type') in ['信托计划', '资管计划', '私募基金']:
                    level = max(level, 2)
                    if asset.get('underlying'):
                        level = max(level, 3)
        return level
    
    def _check_investment_restrictions(self, product: TrustProduct) -> List[Dict]:
        """检查投资限制"""
        issues = []
        return issues
    
    def check_investor_match(self, product: TrustProduct, investor_type: str) -> Dict:
        """检查投资者适当性匹配"""
        allowed_types = self.rules['investor_qualification'].get(product.risk_level, [])
        matched = investor_type in allowed_types
        
        return {
            'matched': matched,
            'product_risk': product.risk_level,
            'investor_type': investor_type,
            'allowed_types': allowed_types,
            'suggestion': '适当性匹配通过' if matched else f'该产品风险等级为{product.risk_level}，不适合{investor_type}投资者'
        }


class ProductFetcher:
    """产品数据获取器（集成数据对接层）"""
    
    def __init__(self):
        self.use_adapter = DATA_ADAPTER_AVAILABLE
        if self.use_adapter:
            self.provider = get_data_provider()
    
    def fetch_products(self, filters: Dict = None) -> List[TrustProduct]:
        """获取产品数据（优先使用数据对接层）"""
        if self.use_adapter:
            try:
                # 使用数据对接层获取数据
                adapter_filters = self._convert_filters(filters)
                products_data = self.provider.get_products(**adapter_filters)
                
                if products_data:
                    print(f"✅ 从数据对接层获取到 {len(products_data)} 个产品")
                    return [TrustProduct.from_data_adapter(p) for p in products_data]
            except Exception as e:
                print(f"数据对接层获取失败: {e}，回退到模拟数据")
        
        # 回退到模拟数据
        return self._fetch_mock_products(filters)
    
    def _convert_filters(self, filters: Dict) -> Dict:
        """转换过滤器格式"""
        if not filters:
            return {}
        
        adapter_filters = {}
        if 'min_yield' in filters:
            adapter_filters['min_yield'] = filters['min_yield']
        if 'max_duration' in filters:
            adapter_filters['max_duration'] = filters['max_duration']
        if 'risk_level' in filters:
            adapter_filters['risk_level'] = filters['risk_level']
        
        return adapter_filters
    
    def _fetch_mock_products(self, filters: Dict = None) -> List[TrustProduct]:
        """获取模拟产品数据"""
        sample_products = [
            TrustProduct(
                product_code="ZG信托-2026-001",
                product_name="中港稳健1号集合资金信托计划",
                issuer="中港信托有限公司",
                trust_type=TrustType.COLLECTIVE.value,
                investment_type=InvestmentType.FIXED_INCOME.value,
                risk_level="R3",
                min_investment=Decimal('1000000'),
                duration=18,
                expected_yield=Decimal('7.2'),
                distribution_way="按季付息",
                scale=Decimal('500000000'),
                underlying_assets=[
                    {'type': '非标债权', 'credit_rating': 'AA+', 'guarantee': '连带责任保证'}
                ]
            ),
            TrustProduct(
                product_code="PA信托-2026-015",
                product_name="平安优享2号集合资金信托计划",
                issuer="平安信托有限责任公司",
                trust_type=TrustType.COLLECTIVE.value,
                investment_type=InvestmentType.MIXED.value,
                risk_level="R3",
                min_investment=Decimal('3000000'),
                duration=24,
                expected_yield=Decimal('8.0'),
                distribution_way="到期一次还本付息",
                scale=Decimal('1000000000'),
                underlying_assets=[
                    {'type': '混合资产', 'credit_rating': 'AA', 'guarantee': '抵押+保证'}
                ]
            )
        ]
        
        for product in sample_products:
            if self._matches_filter(product, filters):
                yield product
    
    def _matches_filter(self, product: TrustProduct, filters: Dict) -> bool:
        """检查产品是否符合筛选条件"""
        if not filters:
            return True
        
        if filters.get('min_yield') and product.expected_yield < filters['min_yield']:
            return False
        if filters.get('max_yield') and product.expected_yield > filters['max_yield']:
            return False
        if filters.get('max_duration') and product.duration > filters['max_duration']:
            return False
        if filters.get('min_duration') and product.duration < filters['min_duration']:
            return False
        if filters.get('risk_level') and product.risk_level not in filters['risk_level']:
            return False
        if filters.get('trust_type') and product.trust_type != filters['trust_type']:
            return False
        if filters.get('investment_type') and product.investment_type != filters['investment_type']:
            return False
        
        return True


class TrustProductAnalyzer:
    """信托产品分析器主类（更新版）"""
    
    def __init__(self):
        self.fetcher = ProductFetcher()
        self.risk_engine = RiskAssessmentEngine()
        self.compliance_checker = ComplianceChecker()
    
    def analyze(self, product_code: str = None, filters: Dict = None) -> Dict:
        """分析信托产品"""
        products = list(self.fetcher.fetch_products(filters))
        
        if product_code:
            product = next((p for p in products if p.product_code == product_code), None)
        else:
            product = products[0] if products else None
        
        if not product:
            return {
                'status': 'error',
                'message': '未找到符合条件的信托产品'
            }
        
        risk_assessment = self.risk_engine.calculate_overall_risk(product)
        compliance = self.compliance_checker.check_compliance(product)
        underlying_analysis = self._analyze_underlying(product)
        
        # 添加数据源信息
        data_source = "数据对接层" if self.fetcher.use_adapter else "模拟数据"
        
        return {
            'status': 'success',
            'data': {
                'product': product.to_dict(),
                'risk_assessment': risk_assessment,
                'compliance_check': compliance,
                'underlying_analysis': underlying_analysis
            },
            'metadata': {
                'source': 'trust-product-analyzer',
                'data_source': data_source,
                'version': '1.1.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def compare(self, product_codes: List[str]) -> Dict:
        """对比多个信托产品"""
        products = list(self.fetcher.fetch_products({}))
        selected = [p for p in products if p.product_code in product_codes]
        
        analyzed = []
        for product in selected:
            risk = self.risk_engine.calculate_overall_risk(product)
            analyzed.append({
                'product': product.to_dict(),
                'risk_assessment': risk
            })
        
        return {
            'status': 'success',
            'data': {
                'products': analyzed,
                'comparison': self._generate_comparison(analyzed)
            },
            'metadata': {
                'source': 'trust-product-analyzer',
                'version': '1.1.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def screen(self, filters: Dict) -> Dict:
        """筛选信托产品"""
        products = list(self.fetcher.fetch_products(filters))
        
        analyzed_products = []
        for product in products:
            risk = self.risk_engine.calculate_overall_risk(product)
            compliance = self.compliance_checker.check_compliance(product)
            
            analyzed_products.append({
                'product': product.to_dict(),
                'risk_score': risk['overall_score'],
                'compliance_passed': compliance['passed'],
                'risk_adjusted_yield': float(product.expected_yield) * (risk['overall_score'] / 100)
            })
        
        analyzed_products.sort(key=lambda x: x['risk_adjusted_yield'], reverse=True)
        
        return {
            'status': 'success',
            'data': {
                'total': len(analyzed_products),
                'products': analyzed_products
            },
            'filters': filters,
            'metadata': {
                'source': 'trust-product-analyzer',
                'version': '1.1.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _analyze_underlying(self, product: TrustProduct) -> Dict:
        """分析底层资产"""
        assets = product.underlying_assets or []
        concentration = len(assets) / 10 if assets else 0
        
        ratings = []
        for asset in assets:
            rating = asset.get('credit_rating', '')
            if rating:
                ratings.append(rating)
        
        return {
            'asset_count': len(assets),
            'concentration': round(min(concentration, 1.0), 2),
            'credit_ratings': ratings,
            'credit_quality': ratings[0] if ratings else '未知'
        }
    
    def _generate_comparison(self, products: List[Dict]) -> Dict:
        """生成产品对比分析"""
        if len(products) < 2:
            return {}
        
        return {
            'yield_comparison': {
                'highest': max(p['product']['expected_yield'] for p in products),
                'lowest': min(p['product']['expected_yield'] for p in products),
                'average': round(sum(p['product']['expected_yield'] for p in products) / len(products), 2)
            },
            'risk_comparison': {
                'safest': max(p['risk_assessment']['overall_score'] for p in products),
                'riskiest': min(p['risk_assessment']['overall_score'] for p in products)
            }
        }


def main():
    parser = argparse.ArgumentParser(description='信托产品综合分析器 v1.1（集成数据对接）')
    parser.add_argument('--action', choices=['analyze', 'compare', 'screen'], required=True)
    parser.add_argument('--product-code', help='产品代码')
    parser.add_argument('--codes', help='多个产品代码，逗号分隔')
    parser.add_argument('--min-yield', type=float, help='最低预期收益')
    parser.add_argument('--max-yield', type=float, help='最高预期收益')
    parser.add_argument('--min-duration', type=int, help='最短期限（月）')
    parser.add_argument('--max-duration', type=int, help='最长期限（月）')
    parser.add_argument('--risk-level', help='风险等级，如R2,R3')
    parser.add_argument('--output', default='json', choices=['json', 'markdown'])
    
    args = parser.parse_args()
    
    analyzer = TrustProductAnalyzer()
    
    if args.action == 'analyze':
        if not args.product_code:
            print("错误：分析操作需要提供 --product-code 参数", file=sys.stderr)
            sys.exit(1)
        result = analyzer.analyze(product_code=args.product_code)
    
    elif args.action == 'compare':
        if not args.codes:
            print("错误：对比操作需要提供 --codes 参数", file=sys.stderr)
            sys.exit(1)
        codes = [c.strip() for c in args.codes.split(',')]
        result = analyzer.compare(codes)
    
    elif args.action == 'screen':
        filters = {
            'min_yield': args.min_yield,
            'max_yield': args.max_yield,
            'min_duration': args.min_duration,
            'max_duration': args.max_duration,
            'risk_level': args.risk_level.split(',') if args.risk_level else None
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        result = analyzer.screen(filters)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
