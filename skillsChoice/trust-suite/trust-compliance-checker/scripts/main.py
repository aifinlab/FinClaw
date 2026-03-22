#!/usr/bin/env python3
"""
信托合规审查器
Trust Compliance Checker

功能：合格投资者检查、嵌套穿透、投资限制、关联交易识别
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

import networkx as nx


class InvestorType(Enum):
    """投资者类型"""
    INDIVIDUAL = "自然人"
    INSTITUTION = "机构"
    PRODUCT = "资管产品"


class TrustType(Enum):
    """信托类型"""
    COLLECTIVE = "集合信托"
    SINGLE = "单一信托"
    PROPERTY = "财产权信托"


@dataclass
class Investor:
    """投资者信息"""
    name: str
    investor_type: str
    financial_assets: float  # 金融资产（万元）
    annual_income: float     # 年收入（万元）
    investment_experience: int = 0  # 投资经验（年）
    risk_tolerance: str = "稳健型"
    net_worth: float = 0     # 净资产


@dataclass
class TrustProduct:
    """信托产品"""
    product_code: str
    product_name: str
    trust_type: str
    min_investment: float
    risk_level: str
    investment_scope: List[str]
    distribution_method: str
    duration: int


@dataclass
class InvestmentNode:
    """投资节点"""
    node_id: str
    name: str
    node_type: str  # 信托/资管/基金/底层资产
    amount: float
    children: List['InvestmentNode'] = None
    underlying_assets: List[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class QualifiedInvestorChecker:
    """合格投资者检查器"""
    
    # 合格投资者标准（监管规定）
    QUALIFICATION_STANDARDS = {
        '自然人': {
            'financial_assets': 500,  # 500万元
            'annual_income': 40,      # 40万元/年（连续三年）
            'net_worth': 1000         # 1000万元
        },
        '机构': {
            'net_assets': 1000        # 1000万元
        }
    }
    
    # 适当性匹配
    APPROPRIATENESS_MATRIX = {
        'R1': ['谨慎型', '稳健型', '平衡型', '进取型', '激进型'],
        'R2': ['稳健型', '平衡型', '进取型', '激进型'],
        'R3': ['平衡型', '进取型', '激进型'],
        'R4': ['进取型', '激进型'],
        'R5': ['激进型']
    }
    
    def check(self, investor: Investor, product: TrustProduct) -> Dict:
        """执行合格投资者和适当性检查"""
        results = {
            'qualified_investor': self._check_qualified_investor(investor),
            'appropriateness': self._check_appropriateness(investor, product),
            'min_investment': self._check_min_investment(investor, product)
        }
        
        # 综合判断
        all_passed = all(r['passed'] for r in results.values())
        
        return {
            'passed': all_passed,
            'score': self._calculate_compliance_score(results),
            'details': results,
            'recommendations': self._generate_recommendations(results)
        }
    
    def _check_qualified_investor(self, investor: Investor) -> Dict:
        """检查是否为合格投资者"""
        standard = self.QUALIFICATION_STANDARDS.get(investor.investor_type, {})
        
        checks = []
        
        if 'financial_assets' in standard:
            passed = investor.financial_assets >= standard['financial_assets']
            checks.append({
                'item': '金融资产',
                'required': f"≥{standard['financial_assets']}万元",
                'actual': f"{investor.financial_assets}万元",
                'passed': passed
            })
        
        if 'annual_income' in standard:
            passed = investor.annual_income >= standard['annual_income']
            checks.append({
                'item': '年收入',
                'required': f"≥{standard['annual_income']}万元/年",
                'actual': f"{investor.annual_income}万元/年",
                'passed': passed
            })
        
        if 'net_worth' in standard and investor.net_worth > 0:
            passed = investor.net_worth >= standard['net_worth']
            checks.append({
                'item': '净资产',
                'required': f"≥{standard['net_worth']}万元",
                'actual': f"{investor.net_worth}万元",
                'passed': passed
            })
        
        # 满足任一条件即可
        passed = any(c['passed'] for c in checks)
        
        return {
            'passed': passed,
            'checks': checks,
            'conclusion': '符合合格投资者标准' if passed else '不符合合格投资者标准'
        }
    
    def _check_appropriateness(self, investor: Investor, product: TrustProduct) -> Dict:
        """检查适当性匹配"""
        allowed_types = self.APPROPRIATENESS_MATRIX.get(product.risk_level, [])
        matched = investor.risk_tolerance in allowed_types
        
        return {
            'passed': matched,
            'product_risk_level': product.risk_level,
            'investor_risk_tolerance': investor.risk_tolerance,
            'allowed_types': allowed_types,
            'conclusion': f'风险等级{product.risk_level}与投资者类型{investor.risk_tolerance}' + 
                         ('匹配' if matched else '不匹配')
        }
    
    def _check_min_investment(self, investor: Investor, product: TrustProduct) -> Dict:
        """检查起投金额"""
        # 这里简化处理，实际需要看投资者实际投资金额
        return {
            'passed': True,  # 假设已通过其他方式验证
            'min_required': product.min_investment,
            'note': '需在认购时验证实际投资金额'
        }
    
    def _calculate_compliance_score(self, results: Dict) -> int:
        """计算合规分数"""
        score = 100
        if not results['qualified_investor']['passed']:
            score -= 40
        if not results['appropriateness']['passed']:
            score -= 30
        return max(0, score)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if not results['qualified_investor']['passed']:
            recommendations.append('建议投资者提供补充资产证明或选择更低风险等级的产品')
        
        if not results['appropriateness']['passed']:
            recommendations.append('建议重新进行风险测评或推荐匹配投资者风险偏好的产品')
        
        return recommendations


class NestedStructureChecker:
    """嵌套结构检查器"""
    
    MAX_NESTED_LAYERS = 2  # 最大嵌套层数
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def check(self, root_node: InvestmentNode) -> Dict:
        """检查嵌套结构"""
        # 构建图
        self._build_graph(root_node)
        
        # 计算层数
        max_depth = self._calculate_max_depth(root_node.node_id)
        
        # 穿透底层资产
        underlying = self._get_underlying_assets(root_node)
        
        # 识别循环嵌套
        cycles = list(nx.simple_cycles(self.graph))
        
        # 合规判断
        issues = []
        if max_depth > self.MAX_NESTED_LAYERS:
            issues.append(f'嵌套层数{max_depth}层超过{self.MAX_NESTED_LAYERS}层限制')
        
        if cycles:
            issues.append(f'发现{cycles}处循环嵌套')
        
        return {
            'passed': len(issues) == 0,
            'max_layers': max_depth,
            'underlying_assets': underlying,
            'cycles_detected': len(cycles) > 0,
            'issues': issues,
            'structure_map': self._generate_structure_map(root_node)
        }
    
    def _build_graph(self, node: InvestmentNode, parent_id: str = None):
        """构建图结构"""
        self.graph.add_node(node.node_id, name=node.name, type=node.node_type)
        
        if parent_id:
            self.graph.add_edge(parent_id, node.node_id, amount=node.amount)
        
        for child in node.children:
            self._build_graph(child, node.node_id)
    
    def _calculate_max_depth(self, root_id: str) -> int:
        """计算最大深度"""
        if root_id not in self.graph:
            return 1
        
        max_depth = 1
        for node in self.graph.nodes():
            if nx.has_path(self.graph, root_id, node):
                path_length = nx.shortest_path_length(self.graph, root_id, node)
                max_depth = max(max_depth, path_length + 1)
        
        return max_depth
    
    def _get_underlying_assets(self, node: InvestmentNode) -> List[str]:
        """获取底层资产"""
        assets = []
        
        if node.underlying_assets:
            assets.extend(node.underlying_assets)
        
        for child in node.children:
            assets.extend(self._get_underlying_assets(child))
        
        return list(set(assets))
    
    def _generate_structure_map(self, node: InvestmentNode, depth: int = 0) -> Dict:
        """生成结构映射"""
        return {
            'name': node.name,
            'type': node.node_type,
            'amount': node.amount,
            'depth': depth,
            'children': [self._generate_structure_map(child, depth + 1) 
                        for child in node.children]
        }


class InvestmentLimitChecker:
    """投资限制检查器"""
    
    # 投资限制规则
    LIMIT_RULES = {
        'single_non_standard': 0.15,  # 单一非标15%
        'real_estate': 0.30,          # 房地产30%
        'securities': 0.25,           # 证券25%
        'financial_products': 0.50,   # 金融产品50%
        'related_party': 0.30         # 关联交易30%
    }
    
    def check(self, investments: List[Dict], total_scale: float) -> Dict:
        """检查投资限制"""
        checks = []
        
        # 计算各类投资占比
        by_category = self._categorize_investments(investments)
        
        # 检查单一非标集中度
        for inv in investments:
            if inv.get('type') == '非标债权':
                ratio = inv['amount'] / total_scale
                passed = ratio <= self.LIMIT_RULES['single_non_standard']
                checks.append({
                    'item': f"单一非标债权-{inv.get('name', '')}",
                    'limit': f"≤{self.LIMIT_RULES['single_non_standard']*100}%",
                    'actual': f"{ratio*100:.2f}%",
                    'passed': passed
                })
        
        # 检查房地产集中度
        real_estate_total = sum(inv['amount'] for inv in investments 
                               if inv.get('category') == '房地产')
        real_estate_ratio = real_estate_total / total_scale
        checks.append({
            'item': '房地产集中度',
            'limit': f"≤{self.LIMIT_RULES['real_estate']*100}%",
            'actual': f"{real_estate_ratio*100:.2f}%",
            'passed': real_estate_ratio <= self.LIMIT_RULES['real_estate']
        })
        
        # 检查证券类投资
        securities_total = sum(inv['amount'] for inv in investments
                              if inv.get('type') in ['股票', '债券', '基金'])
        securities_ratio = securities_total / total_scale
        checks.append({
            'item': '证券类投资',
            'limit': f"≤{self.LIMIT_RULES['securities']*100}%",
            'actual': f"{securities_ratio*100:.2f}%",
            'passed': securities_ratio <= self.LIMIT_RULES['securities']
        })
        
        all_passed = all(c['passed'] for c in checks)
        
        return {
            'passed': all_passed,
            'checks': checks,
            'category_breakdown': by_category
        }
    
    def _categorize_investments(self, investments: List[Dict]) -> Dict:
        """按类别统计投资"""
        categories = {}
        for inv in investments:
            cat = inv.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + inv['amount']
        return categories


class RelatedPartyChecker:
    """关联交易检查器"""
    
    def __init__(self):
        self.related_parties: Set[str] = set()
    
    def add_related_party(self, entity: str):
        """添加关联方"""
        self.related_parties.add(entity)
    
    def check(self, transactions: List[Dict]) -> Dict:
        """检查关联交易"""
        related_transactions = []
        
        for txn in transactions:
            counterparty = txn.get('counterparty', '')
            if counterparty in self.related_parties:
                related_transactions.append({
                    'transaction_id': txn.get('id'),
                    'counterparty': counterparty,
                    'amount': txn.get('amount'),
                    'type': txn.get('type')
                })
        
        total_related = sum(t['amount'] for t in related_transactions)
        
        return {
            'related_transactions_found': len(related_transactions) > 0,
            'count': len(related_transactions),
            'total_amount': total_related,
            'transactions': related_transactions,
            'disclosure_required': len(related_transactions) > 0,
            'note': '发现关联交易需在合同中披露并取得投资者同意'
        }


class TrustComplianceChecker:
    """信托合规审查主类"""
    
    def __init__(self):
        self.qualified_checker = QualifiedInvestorChecker()
        self.nested_checker = NestedStructureChecker()
        self.limit_checker = InvestmentLimitChecker()
        self.related_checker = RelatedPartyChecker()
    
    def check_product(self, product: TrustProduct, investments: List[Dict]) -> Dict:
        """产品合规检查"""
        results = {
            'product_basic': self._check_product_basic(product),
            'investment_limits': self.limit_checker.check(
                investments, 
                product.min_investment * 100  # 假设规模为起投的100倍
            )
        }
        
        all_passed = all(r.get('passed', True) for r in results.values())
        
        return {
            'status': 'success',
            'check_type': 'product',
            'overall_compliance': '合规' if all_passed else '不合规',
            'score': self._calculate_overall_score(results),
            'details': results,
            'metadata': {
                'source': 'trust-compliance-checker',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def check_investor(self, investor: Investor, product: TrustProduct) -> Dict:
        """投资者合规检查"""
        result = self.qualified_checker.check(investor, product)
        
        return {
            'status': 'success',
            'check_type': 'investor',
            'overall_compliance': '合规' if result['passed'] else '不合规',
            'score': result['score'],
            'details': result,
            'metadata': {
                'source': 'trust-compliance-checker',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def check_nested_structure(self, root_node: InvestmentNode) -> Dict:
        """嵌套结构检查"""
        result = self.nested_checker.check(root_node)
        
        return {
            'status': 'success',
            'check_type': 'nested',
            'overall_compliance': '合规' if result['passed'] else '不合规',
            'details': result,
            'metadata': {
                'source': 'trust-compliance-checker',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def check_transactions(self, transactions: List[Dict], related_parties: List[str] = None) -> Dict:
        """交易合规检查"""
        if related_parties:
            for party in related_parties:
                self.related_checker.add_related_party(party)
        
        result = self.related_checker.check(transactions)
        
        return {
            'status': 'success',
            'check_type': 'transaction',
            'overall_compliance': '合规' if not result['related_transactions_found'] else '需关注',
            'details': result,
            'metadata': {
                'source': 'trust-compliance-checker',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _check_product_basic(self, product: TrustProduct) -> Dict:
        """检查产品基本信息"""
        issues = []
        
        # 检查期限
        if product.duration > 60:  # 5年
            issues.append('产品期限超过5年，需特别关注流动性安排')
        
        # 检查投资范围
        prohibited = ['非上市股权', '限制性行业']
        for scope in product.investment_scope:
            if scope in prohibited:
                issues.append(f'投资范围包含受限类别：{scope}')
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def _calculate_overall_score(self, results: Dict) -> int:
        """计算整体合规分数"""
        scores = []
        for key, result in results.items():
            if isinstance(result, dict) and 'passed' in result:
                scores.append(100 if result['passed'] else 50)
        
        return int(sum(scores) / len(scores)) if scores else 100


def main():
    parser = argparse.ArgumentParser(description='信托合规审查器')
    parser.add_argument('--check-type', required=True,
                       choices=['product', 'investor', 'nested', 'transaction'],
                       help='检查类型')
    parser.add_argument('--product', help='产品信息文件')
    parser.add_argument('--investor', help='投资者信息文件')
    parser.add_argument('--structure', help='嵌套结构文件')
    parser.add_argument('--transactions', help='交易记录文件')
    parser.add_argument('--output', default='json', choices=['json'])
    
    args = parser.parse_args()
    
    checker = TrustComplianceChecker()
    
    if args.check_type == 'product':
        if not args.product:
            print("错误：产品检查需要提供 --product 参数")
            sys.exit(1)
        
        with open(args.product, 'r') as f:
            data = json.load(f)
        
        product = TrustProduct(**data['product'])
        investments = data.get('investments', [])
        result = checker.check_product(product, investments)
    
    elif args.check_type == 'investor':
        if not args.investor or not args.product:
            print("错误：投资者检查需要提供 --investor 和 --product 参数")
            sys.exit(1)
        
        with open(args.investor, 'r') as f:
            inv_data = json.load(f)
        with open(args.product, 'r') as f:
            prod_data = json.load(f)
        
        investor = Investor(**inv_data)
        product = TrustProduct(**prod_data['product'])
        result = checker.check_investor(investor, product)
    
    elif args.check_type == 'nested':
        if not args.structure:
            print("错误：嵌套检查需要提供 --structure 参数")
            sys.exit(1)
        
        # 简化处理，实际需要解析嵌套结构
        result = {'status': 'success', 'message': '嵌套结构检查需实现结构解析'}
    
    elif args.check_type == 'transaction':
        if not args.transactions:
            print("错误：交易检查需要提供 --transactions 参数")
            sys.exit(1)
        
        with open(args.transactions, 'r') as f:
            transactions = json.load(f)
        
        result = checker.check_transactions(transactions)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
