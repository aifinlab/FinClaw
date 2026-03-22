#!/usr/bin/env python3
"""
信托产品综合分析器
Trust Product Analyzer

功能：信托产品信息抓取、风险评级、收益测算、合规检查
"""

import argparse
import json
import sys
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
    
    def __init__(self, code, name, investor_type):
        self.code = code
        self.name = name
        self.investor_type = investor_type


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
    duration: int  # 月
    expected_yield: Decimal
    distribution_way: str
    scale: Decimal  # 发行规模
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
        # 基于底层资产、担保措施、融资主体评级
        score = 70  # 基础分
        
        # 分析底层资产
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
                
                # 担保措施
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
        
        # 根据投资类型调整
        risk_factors = {
            InvestmentType.FIXED_INCOME.value: 0,
            InvestmentType.MIXED.value: -10,
            InvestmentType.EQUITY.value: -20,
            InvestmentType.ALTERNATIVE.value: -25
        }
        
        score += risk_factors.get(product.investment_type, 0)
        
        # 久期风险
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
        
        # 期限越长流动性越差
        if product.duration > 36:
            score -= 20
        elif product.duration > 24:
            score -= 10
        elif product.duration > 12:
            score -= 5
        
        # 开放/封闭式
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
            'nested_limit': 2,  # 嵌套层数限制
            'min_investment': {
                'collective': 300000,  # 集合信托30万起
                'single': 1000000      # 单一信托100万起
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
        
        # 检查起投金额
        min_required = self.rules['min_investment'].get(
            'collective' if product.trust_type == TrustType.COLLECTIVE.value else 'single'
        )
        if product.min_investment < min_required:
            issues.append({
                'type': '起投金额不足',
                'severity': 'high',
                'description': f'起投金额{product.min_investment}低于最低要求{min_required}'
            })
        
        # 检查嵌套层数
        nested_level = self._check_nested_level(product)
        if nested_level > self.rules['nested_limit']:
            issues.append({
                'type': '嵌套层数超限',
                'severity': 'high',
                'description': f'嵌套层数{nested_level}超过限制{self.rules["nested_limit"]}'
            })
        
        # 检查投资限制
        investment_issues = self._check_investment_restrictions(product)
        issues.extend(investment_issues)
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'nested_level': nested_level
        }
    
    def _check_nested_level(self, product: TrustProduct) -> int:
        """检查嵌套层数"""
        # 简化的嵌套层数检查逻辑
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
        # 检查非标债权投资比例、房地产集中度等
        # 这里简化处理，实际需要根据监管规定详细检查
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
    """产品数据抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_from_yongyi(self, product_code: str = None, filters: Dict = None) -> List[TrustProduct]:
        """从用益信托网抓取产品数据"""
        # 这里使用模拟数据，实际实现需要对接真实数据源
        products = []
        
        # 模拟数据
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
                    {
                        'type': '非标债权',
                        'credit_rating': 'AA+',
                        'guarantee': '连带责任保证'
                    }
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
                    {
                        'type': '混合资产',
                        'credit_rating': 'AA',
                        'guarantee': '抵押+保证'
                    }
                ]
            )
        ]
        
        # 应用筛选条件
        for product in sample_products:
            if self._matches_filter(product, filters):
                products.append(product)
        
        return products
    
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
    """信托产品分析器主类"""
    
    def __init__(self):
        self.fetcher = ProductFetcher()
        self.risk_engine = RiskAssessmentEngine()
        self.compliance_checker = ComplianceChecker()
    
    def analyze(self, product_code: str = None, filters: Dict = None) -> Dict:
        """分析信托产品"""
        # 获取产品数据
        if product_code:
            products = self.fetcher.fetch_from_yongyi(product_code=product_code)
            product = next((p for p in products if p.product_code == product_code), None)
        else:
            products = self.fetcher.fetch_from_yongyi(filters=filters)
            product = products[0] if products else None
        
        if not product:
            return {
                'status': 'error',
                'message': '未找到符合条件的信托产品'
            }
        
        # 风险评估
        risk_assessment = self.risk_engine.calculate_overall_risk(product)
        
        # 合规检查
        compliance = self.compliance_checker.check_compliance(product)
        
        # 底层资产分析
        underlying_analysis = self._analyze_underlying(product)
        
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
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def compare(self, product_codes: List[str]) -> Dict:
        """对比多个信托产品"""
        products = []
        for code in product_codes:
            result = self.analyze(product_code=code)
            if result['status'] == 'success':
                products.append(result['data'])
        
        # 生成对比表格
        comparison = self._generate_comparison(products)
        
        return {
            'status': 'success',
            'data': {
                'products': products,
                'comparison': comparison
            },
            'metadata': {
                'source': 'trust-product-analyzer',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def screen(self, filters: Dict) -> Dict:
        """筛选信托产品"""
        products = self.fetcher.fetch_from_yongyi(filters=filters)
        
        # 对筛选结果进行分析排序
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
        
        # 按风险调整后收益排序
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
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _analyze_underlying(self, product: TrustProduct) -> Dict:
        """分析底层资产"""
        assets = product.underlying_assets or []
        
        concentration = len(assets) / 10 if assets else 0  # 简化集中度计算
        
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
        
        comparison = {
            'yield_comparison': {
                'highest': max(p['product']['expected_yield'] for p in products),
                'lowest': min(p['product']['expected_yield'] for p in products),
                'average': round(sum(p['product']['expected_yield'] for p in products) / len(products), 2)
            },
            'risk_comparison': {
                'safest': max(p['risk_assessment']['overall_score'] for p in products),
                'riskiest': min(p['risk_assessment']['overall_score'] for p in products)
            },
            'duration_comparison': {
                'longest': max(p['product']['duration'] for p in products),
                'shortest': min(p['product']['duration'] for p in products)
            },
            'recommendation': self._generate_recommendation(products)
        }
        
        return comparison
    
    def _generate_recommendation(self, products: List[Dict]) -> str:
        """生成推荐建议"""
        # 按风险调整后收益排序推荐
        sorted_products = sorted(
            products,
            key=lambda x: x['product']['expected_yield'] * (x['risk_assessment']['overall_score'] / 100),
            reverse=True
        )
        
        if sorted_products:
            best = sorted_products[0]['product']
            return f"综合风险收益比，推荐{best['product_name']}({best['product_code']})，预期收益{best['expected_yield']}%"
        
        return "暂无推荐"


def main():
    parser = argparse.ArgumentParser(description='信托产品综合分析器')
    parser.add_argument('--action', choices=['analyze', 'compare', 'screen'], required=True,
                       help='操作类型：analyze分析单个产品, compare对比产品, screen筛选产品')
    parser.add_argument('--product-code', help='产品代码')
    parser.add_argument('--codes', help='多个产品代码，逗号分隔')
    parser.add_argument('--min-yield', type=float, help='最低预期收益')
    parser.add_argument('--max-yield', type=float, help='最高预期收益')
    parser.add_argument('--min-duration', type=int, help='最短期限（月）')
    parser.add_argument('--max-duration', type=int, help='最长期限（月）')
    parser.add_argument('--risk-level', help='风险等级，如R2,R3')
    parser.add_argument('--output', default='json', choices=['json', 'markdown'],
                       help='输出格式')
    
    args = parser.parse_args()
    
    analyzer = TrustProductAnalyzer()
    
    if args.action == 'analyze':
        if not args.product_code:
            print("错误：分析操作需要提供 --product-code 参数", file=sys.stderr)
            sys.exit(1)
        
        result = analyzer.analyze(product_code=args.product_code)
    
    elif args.action == 'compare':
        if not args.codes:
            print("错误：对比操作需要提供 --codes 参数，多个代码用逗号分隔", file=sys.stderr)
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
        # 移除None值
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = analyzer.screen(filters)
    
    # 输出结果
    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Markdown格式输出
        print(format_as_markdown(result))


def format_as_markdown(result: Dict) -> str:
    """格式化为Markdown报告"""
    lines = []
    lines.append("# 信托产品分析报告")
    lines.append("")
    
    if result.get('status') != 'success':
        lines.append(f"**错误**: {result.get('message', '未知错误')}")
        return "\n".join(lines)
    
    data = result.get('data', {})
    
    if 'product' in data:
        product = data['product']
        lines.append(f"## {product['product_name']}")
        lines.append("")
        lines.append(f"- **产品代码**: {product['product_code']}")
        lines.append(f"- **发行机构**: {product['issuer']}")
        lines.append(f"- **产品类型**: {product['trust_type']}")
        lines.append(f"- **投资类型**: {product['investment_type']}")
        lines.append(f"- **风险等级**: {product['risk_level']}")
        lines.append(f"- **起投金额**: {product['min_investment']:,.0f}元")
        lines.append(f"- **产品期限**: {product['duration']}个月")
        lines.append(f"- **预期收益**: {product['expected_yield']}%")
        lines.append(f"- **分配方式**: {product['distribution_way']}")
        lines.append("")
        
        if 'risk_assessment' in data:
            risk = data['risk_assessment']
            lines.append("### 风险评估")
            lines.append("")
            lines.append(f"- **综合评分**: {risk['overall_score']}/100")
            lines.append(f"- **风险等级**: {risk['overall_level']}")
            lines.append(f"- **信用风险**: {risk['credit_risk']['score']}/100 ({risk['credit_risk']['level']})")
            lines.append(f"- **市场风险**: {risk['market_risk']['score']}/100 ({risk['market_risk']['level']})")
            lines.append(f"- **流动性风险**: {risk['liquidity_risk']['score']}/100 ({risk['liquidity_risk']['level']})")
            lines.append("")
    
    lines.append("---")
    lines.append(f"*报告生成时间: {result.get('metadata', {}).get('timestamp', '')}*")
    
    return "\n".join(lines)


if __name__ == '__main__':
    main()
