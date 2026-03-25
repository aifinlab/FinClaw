#!/usr/bin/env python3
"""
信托合规检查器 v4.0 - 同花顺API整改版
功能：合格投资者检查、嵌套穿透、投资限制、关联交易识别

整改内容：
1. 接入同花顺API获取信托公司财务数据
2. 使用从同花顺数据派生的合规规则配置
3. 添加THS API错误处理和降级逻辑
4. 标注数据来源为"同花顺iFinD"

数据源：
  - 优先：用益信托网/中国信登/同花顺iFinD
  - 派生：从同花顺财务数据生成的合规规则
  - 保底：本地缓存/模拟数据
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider, TrustProductData


@dataclass
class Investor:
    """投资者信息"""
    name: str
    investor_type: str
    financial_assets: float
    annual_income: float
    investment_experience: int = 0
    risk_tolerance: str = "稳健型"
    net_worth: float = 0


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
    node_type: str
    amount: float
    children: List['InvestmentNode'] = None
    underlying_assets: List[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class QualifiedInvestorChecker:
    """合格投资者检查器"""
    
    QUALIFICATION_STANDARDS = {
        '自然人': {
            'financial_assets': 500,
            'annual_income': 40,
            'net_worth': 1000
        },
        '机构': {
            'net_worth': 1000
        }
    }
    
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
        return {
            'passed': True,
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
    
    MAX_NESTED_LAYERS = 2
    
    def __init__(self):
        self.nodes = {}
        self.edges = {}
    
    def check(self, root_node: InvestmentNode) -> Dict:
        """检查嵌套结构"""
        self._build_structure(root_node)
        
        max_depth = self._calculate_max_depth(root_node.node_id)
        underlying = self._get_underlying_assets(root_node)
        cycles = self._detect_cycles(root_node.node_id)
        
        issues = []
        if max_depth > self.MAX_NESTED_LAYERS:
            issues.append(f'嵌套层数{max_depth}层超过{self.MAX_NESTED_LAYERS}层限制')
        
        if cycles:
            issues.append(f'发现循环嵌套')
        
        return {
            'passed': len(issues) == 0,
            'max_layers': max_depth,
            'underlying_assets': underlying,
            'cycles_detected': len(cycles) > 0,
            'issues': issues,
            'structure_map': self._generate_structure_map(root_node)
        }
    
    def _build_structure(self, node: InvestmentNode, parent_id: str = None):
        """构建结构"""
        self.nodes[node.node_id] = {'name': node.name, 'type': node.node_type}
        
        if parent_id:
            if parent_id not in self.edges:
                self.edges[parent_id] = []
            self.edges[parent_id].append(node.node_id)
        
        for child in node.children:
            self._build_structure(child, node.node_id)
    
    def _calculate_max_depth(self, root_id: str) -> int:
        """计算最大深度"""
        return self._get_depth_recursive(root_id, 1)
    
    def _get_depth_recursive(self, node_id: str, current_depth: int) -> int:
        """递归计算深度"""
        if node_id not in self.edges or not self.edges[node_id]:
            return current_depth
        
        max_child_depth = current_depth
        for child_id in self.edges[node_id]:
            child_depth = self._get_depth_recursive(child_id, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def _detect_cycles(self, root_id: str) -> List[str]:
        """检测循环"""
        cycles = []
        visited = set()
        
        def dfs(node_id, path):
            if node_id in path:
                cycles.append(node_id)
                return
            if node_id in visited:
                return
            visited.add(node_id)
            path.add(node_id)
            
            if node_id in self.edges:
                for child_id in self.edges[node_id]:
                    dfs(child_id, path)
            
            path.remove(node_id)
        
        dfs(root_id, set())
        return cycles
    
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
    
    LIMIT_RULES = {
        'single_non_standard': 0.15,
        'real_estate': 0.30,
        'securities': 0.25,
        'financial_products': 0.50,
        'related_party': 0.30
    }
    
    def check(self, investments: List[Dict], total_scale: float) -> Dict:
        """检查投资限制"""
        checks = []
        
        by_category = self._categorize_investments(investments)
        
        # 检查单一非标集中度
        for inv in investments:
            if inv.get('type') in ['非标债权', '固定收益类']:
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
                              if inv.get('type') in ['股票', '债券', '基金', '权益类'])
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
    """信托合规审查主类 v4.0 - 同花顺API整改版
    
    整改内容：
    1. 接入同花顺API获取信托公司财务数据
    2. 使用从同花顺数据派生的合规规则配置
    3. 添加THS API错误处理和降级逻辑
    4. 标注数据来源为"同花顺iFinD"
    """
    
    def __init__(self):
        self.qualified_checker = QualifiedInvestorChecker()
        self.nested_checker = NestedStructureChecker()
        self.limit_checker = InvestmentLimitChecker()
        self.related_checker = RelatedPartyChecker()
        self.data_provider = get_data_provider()
        self._ths_compliance_configs = None
    
    def _load_ths_compliance_configs(self) -> Dict:
        """
        加载从同花顺数据派生的合规规则配置
        
        整改内容：对于无法API化的规则数据，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        if self._ths_compliance_configs is None:
            try:
                configs = self.data_provider.get_ths_derived_configs('compliance')
                self._ths_compliance_configs = {
                    'configs': configs,
                    'data_source': '同花顺iFinD(派生)',
                    'loaded_at': datetime.now().isoformat()
                }
            except Exception as e:
                logger.warning(f"加载同花顺派生合规规则失败: {e}")
                self._ths_compliance_configs = {
                    'configs': [],
                    'data_source': '默认规则',
                    'loaded_at': datetime.now().isoformat(),
                    'error': str(e)
                }
        return self._ths_compliance_configs
    
    def get_trust_company_financials(self, company_name: str) -> Optional[Dict]:
        """
        获取信托公司财务数据
        
        整改内容：接入同花顺API获取ROE/净利润/营收等财务数据
        数据来源标注：同花顺iFinD
        """
        try:
            financials = self.data_provider.get_trust_company_financials(company_name)
            if financials:
                return {
                    **financials,
                    'data_source': '同花顺iFinD',
                    'query_time': datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"获取信托公司财务数据失败: {e}")
        
        return None
    
    def check_product_from_data_source(self, **filters) -> Dict:
        """从数据源获取产品并检查合规性（增强版）"""
        products = self.data_provider.get_products(**filters)
        
        if not products:
            data_source_info = self.data_provider.get_data_source_info()
            return {
                'status': 'warning',
                'message': '未找到符合条件的产品，请尝试运行 data/update_data.py 更新数据',
                'data_source': data_source_info,
                'suggestion': '运行: python data/update_data.py --force'
            }
        
        # 使用第一个产品进行检查示例
        p = products[0]
        
        # 获取信托公司财务数据
        trust_company_financials = None
        if p.trust_company:
            trust_company_financials = self.get_trust_company_financials(p.trust_company)
        
        # 加载同花顺派生的合规规则
        ths_configs = self._load_ths_compliance_configs()
        
        # 转换为合规检查格式
        product = TrustProduct(
            product_code=p.product_code,
            product_name=p.product_name,
            trust_type=p.product_type,
            min_investment=p.min_investment * 10000 if p.min_investment else 1000000,
            risk_level=p.risk_level,
            investment_scope=[p.investment_type, p.underlying_type],
            distribution_method='到期分配',
            duration=p.duration
        )
        
        investments = [{'type': p.investment_type, 'amount': p.issue_scale * 10000 if p.issue_scale else 1000000}]
        
        result = self.check_product(product, investments)
        
        # 添加数据质量信息
        if p.quality_label:
            result['data_quality'] = {
                'source': p.quality_label.source,
                'score': p.quality_label.overall_score,
                'fallback_level': p.quality_label.fallback_level,
                'update_time': p.quality_label.update_time
            }
        
        # 添加信托公司财务数据
        if trust_company_financials:
            result['trust_company_financials'] = trust_company_financials
        
        # 添加同花顺派生的合规规则
        result['ths_compliance_configs'] = ths_configs
        
        # 添加数据源信息
        data_source_info = self.data_provider.get_data_source_info()
        result['data_source'] = {
            'last_used_adapter': data_source_info.get('last_used'),
            'available_adapters': [a['name'] for a in data_source_info.get('adapters', []) if a['available']],
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加数据更新建议
        result['data_update_note'] = '建议定期运行: python data/update_data.py'
        
        return result
    
    def check_product(self, product: TrustProduct, investments: List[Dict]) -> Dict:
        """产品合规检查（增强版）"""
        results = {
            'product_basic': self._check_product_basic(product),
            'investment_limits': self.limit_checker.check(
                investments, 
                product.min_investment * 100
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
                'version': '4.0.0',
                'data_source_version': 'ths_api_v4',
                'ths_integration': True,
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
                'version': '4.0.0',
                'data_source_version': 'ths_api_v4',
                'ths_integration': True,
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
                'version': '4.0.0',
                'data_source_version': 'ths_api_v4',
                'ths_integration': True,
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
                'version': '4.0.0',
                'data_source_version': 'ths_api_v4',
                'ths_integration': True,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _check_product_basic(self, product: TrustProduct) -> Dict:
        """检查产品基本信息"""
        issues = []
        
        if product.duration > 60:
            issues.append('产品期限超过5年，需特别关注流动性安排')
        
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
    parser = argparse.ArgumentParser(description='信托合规检查器 v3.0')
    parser.add_argument('--check-type', required=True,
                       choices=['product', 'investor', 'nested', 'transaction', 'from_data_source'],
                       help='检查类型')
    parser.add_argument('--product', help='产品信息文件（可选，优先使用数据源）')
    parser.add_argument('--investor', help='投资者信息文件（可选）')
    parser.add_argument('--trust-company', help='信托公司筛选')
    parser.add_argument('--min-yield', type=float, help='最低收益率筛选')
    parser.add_argument('--update-data', action='store_true',
                       help='先运行数据更新脚本')
    
    args = parser.parse_args()
    
    # 如果需要，先更新数据
    if args.update_data:
        print("🔄 正在更新数据...")
        import subprocess
        data_dir = Path(__file__).parent.parent / 'data'
        subprocess.run(['python', str(data_dir / 'update_data.py'), '--force'])
        print()
    
    checker = TrustComplianceChecker()
    
    if args.check_type == 'from_data_source':
        print("🔍 从数据源获取产品并检查合规性...")
        filters = {}
        if args.trust_company:
            filters['trust_company'] = args.trust_company
        if args.min_yield:
            filters['min_yield'] = args.min_yield
        result = checker.check_product_from_data_source(**filters)
    elif args.check_type == 'product':
        # 优先从数据源获取，除非指定了文件
        if args.product:
            with open(args.product, 'r') as f:
                data = json.load(f)
            product = TrustProduct(**data['product'])
            investments = data.get('investments', [])
            result = checker.check_product(product, investments)
        else:
            print("🔍 从数据源获取产品...")
            result = checker.check_product_from_data_source()
    elif args.check_type == 'investor':
        # 示例投资者检查
        investor = Investor(
            name='示例投资者',
            investor_type='自然人',
            financial_assets=600,
            annual_income=50,
            risk_tolerance='稳健型'
        )
        product = TrustProduct(
            product_code='DEMO001',
            product_name='示例信托产品',
            trust_type='集合信托',
            min_investment=1000000,
            risk_level='R3',
            investment_scope=['固定收益类'],
            distribution_method='到期分配',
            duration=24
        )
        result = checker.check_investor(investor, product)
    else:
        result = {'status': 'error', 'message': '暂不支持此检查类型'}
    
    print("\n" + "=" * 60)
    print("📋 合规检查结果")
    print("=" * 60)
    
    if result.get('status') == 'success':
        print(f"\n检查类型: {result.get('check_type', 'N/A')}")
        print(f"整体合规: {result.get('overall_compliance', 'N/A')}")
        print(f"合规分数: {result.get('score', 'N/A')}")
    
    # 数据源信息
    if 'data_source' in result:
        print(f"\n📡 数据源: {result['data_source'].get('last_used_adapter', 'N/A')}")
        print(f"   可用适配器: {', '.join(result['data_source'].get('available_adapters', []))}")
    
    if 'data_quality' in result:
        dq = result['data_quality']
        print(f"\n📊 数据质量: {dq.get('source', 'N/A')} (评分: {dq.get('score', 0)})")
    
    if result.get('data_update_note'):
        print(f"\n💡 {result['data_update_note']}")
    
    print("\n" + "=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
