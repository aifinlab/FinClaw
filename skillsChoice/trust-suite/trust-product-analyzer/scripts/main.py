#!/usr/bin/env python3
"""
信托产品分析器 - 接入数据适配器 v2.0
功能：产品分析、风险评估、合规检查、收益测算
"""

import argparse
import json
import sys
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider, TrustProductData


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
    underlying_assets: List[Dict] = None
    data_quality: Dict = None  # 数据质量标注
    
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
        score = 70
        
        if product.underlying_assets:
            for asset in product.underlying_assets:
                if asset.get('credit_rating'):
                    rating = asset['credit_rating']
                    if 'AAA' in rating:
                        score += 10
                    elif 'AA' in rating:
                        score += 5
                    else:
                        score -= 5
                
                if asset.get('guarantee'):
                    score += 5
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'level': self._score_to_level(score),
            'factors': ['底层资产质量', '担保措施']
        }
    
    def assess_market_risk(self, product: TrustProduct) -> Dict:
        """市场风险评估"""
        score = 80
        
        risk_factors = {
            '固定收益类': 0,
            '混合类': -10,
            '权益类': -20,
            '商品及金融衍生品类': -25
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
            'factors': ['投资类型', '期限结构']
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
            'factors': ['产品期限', '开放频率']
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
            }
        }
    
    def check_compliance(self, product: TrustProduct) -> Dict:
        """执行合规检查"""
        issues = []
        
        # 检查起投金额
        min_required = self.rules['min_investment'].get(
            'collective' if '集合' in product.trust_type else 'single'
        )
        if product.min_investment < min_required:
            issues.append({
                'type': '起投金额不足',
                'severity': 'high',
                'description': f'起投金额低于最低要求{min_required}'
            })
        
        # 检查嵌套层数
        nested_level = self._check_nested_level(product)
        if nested_level > self.rules['nested_limit']:
            issues.append({
                'type': '嵌套层数超限',
                'severity': 'high',
                'description': f'嵌套层数超过限制'
            })
        
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
        return level


class TrustProductAnalyzer:
    """信托产品分析器主类 - 接入数据适配器"""
    
    def __init__(self):
        self.risk_engine = RiskAssessmentEngine()
        self.compliance_checker = ComplianceChecker()
        self.data_provider = get_data_provider()
    
    def analyze_from_data_source(self, product_code: str = None, 
                                  trust_company: str = None,
                                  min_yield: float = None) -> Dict:
        """
        从数据源获取产品并分析
        
        Args:
            product_code: 产品代码（可选）
            trust_company: 信托公司名称（可选）
            min_yield: 最低收益率筛选（可选）
        
        Returns:
            分析结果，包含数据质量标注
        """
        filters = {}
        if trust_company:
            filters['trust_company'] = trust_company
        if min_yield:
            filters['min_yield'] = min_yield
        
        # 从数据源获取产品
        products = self.data_provider.get_products(**filters)
        
        if not products:
            return {
                'status': 'error',
                'message': '未找到符合条件的产品',
                'data_quality': self.data_provider.get_data_source_info()
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
        
        # 转换为分析用的产品格式
        product_data = self._convert_to_product_format(target_product)
        
        # 执行分析
        return self.analyze(product_data)
    
    def analyze(self, product_data: Dict) -> Dict:
        """分析信托产品"""
        try:
            product = TrustProduct(
                product_code=product_data['product_code'],
                product_name=product_data['product_name'],
                issuer=product_data['issuer'],
                trust_type=product_data['trust_type'],
                investment_type=product_data['investment_type'],
                risk_level=product_data['risk_level'],
                min_investment=Decimal(str(product_data['min_investment'])),
                duration=product_data['duration'],
                expected_yield=Decimal(str(product_data['expected_yield'])),
                distribution_way=product_data['distribution_way'],
                scale=Decimal(str(product_data['scale'])),
                underlying_assets=product_data.get('underlying_assets', []),
                data_quality=product_data.get('data_quality')
            )
        except (KeyError, ValueError) as e:
            return {
                'status': 'error',
                'message': f'产品数据格式错误: {str(e)}'
            }
        
        risk_assessment = self.risk_engine.calculate_overall_risk(product)
        compliance = self.compliance_checker.check_compliance(product)
        
        # 添加数据质量标注
        data_quality = {
            'product_data_source': product_data.get('data_quality', {}).get('source', 'unknown'),
            'product_data_score': product_data.get('data_quality', {}).get('overall_score', 0),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return {
            'status': 'success',
            'data': {
                'product': product.to_dict(),
                'risk_assessment': risk_assessment,
                'compliance_check': compliance
            },
            'data_quality': data_quality,
            'metadata': {
                'source': 'trust-product-analyzer',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _convert_to_product_format(self, data: TrustProductData) -> Dict:
        """将数据源格式转换为分析器格式"""
        return {
            'product_code': data.product_code,
            'product_name': data.product_name,
            'issuer': data.trust_company,
            'trust_type': data.product_type,
            'investment_type': data.investment_type,
            'risk_level': data.risk_level,
            'min_investment': data.min_investment * 10000,  # 转换为元
            'duration': data.duration,
            'expected_yield': data.expected_yield,
            'distribution_way': '到期一次还本付息',
            'scale': data.issue_scale * 10000,  # 转换为元
            'underlying_assets': [{'type': data.underlying_type}] if data.underlying_type else [],
            'data_quality': data.quality_label.to_dict() if data.quality_label else {}
        }


def main():
    parser = argparse.ArgumentParser(description='信托产品综合分析器 v2.0')
    parser.add_argument('--product-file', help='产品数据JSON文件路径')
    parser.add_argument('--product-json', help='产品数据JSON字符串')
    parser.add_argument('--from-data-source', action='store_true', help='从数据源获取产品')
    parser.add_argument('--trust-company', help='信托公司名称筛选')
    parser.add_argument('--min-yield', type=float, help='最低收益率筛选')
    
    args = parser.parse_args()
    
    analyzer = TrustProductAnalyzer()
    
    if args.from_data_source:
        # 从数据源获取并分析
        result = analyzer.analyze_from_data_source(
            trust_company=args.trust_company,
            min_yield=args.min_yield
        )
    elif args.product_file:
        with open(args.product_file, 'r', encoding='utf-8') as f:
            product_data = json.load(f)
        result = analyzer.analyze(product_data)
    elif args.product_json:
        product_data = json.loads(args.product_json)
        result = analyzer.analyze(product_data)
    else:
        # 示例：从数据源获取第一个产品分析
        result = analyzer.analyze_from_data_source(min_yield=6.0)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
