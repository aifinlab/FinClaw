#!/usr/bin/env python3
"""
家族信托架构设计师 v4.0 - 同花顺API整改版
功能：架构设计、传承方案、税务筹划，支持参考同花顺市场数据设计

整改内容：
1. 接入同花顺API获取信托公司财务数据
2. 使用多元金融指数作为信托行业代理
3. 对于无法API化的模板数据，创建从同花顺数据派生的配置
4. 添加THS API错误处理和降级逻辑
5. 标注数据来源为"同花顺iFinD"

数据源：
  - 优先：用益信托网/中国信登/同花顺iFinD
  - 派生：从同花顺数据生成的家族信托配置
  - 保底：本地缓存/模拟数据
"""

import argparse
import json
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider


class FamilyTrustDesigner:
    """家族信托设计主类 v4.0 - 同花顺API整改版
    
    整改内容：
    1. 接入同花顺API获取信托公司财务数据
    2. 使用多元金融指数作为信托行业代理
    3. 对于无法API化的模板数据，创建从同花顺数据派生的配置
    4. 添加THS API错误处理和降级逻辑
    5. 标注数据来源为"同花顺iFinD"
    """
    
    def __init__(self):
        self.data_provider = get_data_provider()
    
    def design(self, client_profile: dict, objectives: list) -> dict:
        """
        设计家族信托方案，参考同花顺市场数据
        
        整改内容：
        - 使用同花顺行业指数作为市场代理
        - 获取信托公司财务数据作为选择依据
        - 数据来源标注：同花顺iFinD
        """
        # 获取市场数据作为参考
        market_stats = self.data_provider.get_market_stats()
        products = self.data_provider.get_products()
        
        # 获取同花顺行业指数
        ths_industry_index = self._get_ths_industry_index()
        
        # 获取信托公司财务数据
        trust_companies = ['平安信托', '中航信托', '五矿信托', '中信信托']
        ths_financials = self._get_trust_companies_financials(trust_companies)
        
        # 获取同花顺派生的配置
        ths_configs = self._get_ths_derived_configs()
        
        # 1. 确定信托类型
        trust_type = self._determine_trust_type(client_profile, objectives)
        
        # 2. 资产注入方案（参考市场产品）
        asset_plan = self._design_asset_plan(client_profile, products, ths_industry_index)
        
        # 3. 分配方案
        distribution = self._design_distribution(client_profile)
        
        # 4. 治理架构
        governance = self._design_governance(client_profile)
        
        # 5. 税务建议
        tax_planning = self._design_tax_planning(client_profile, objectives)
        
        # 6. 投资策略建议（参考同花顺行业数据）
        investment_strategy = self._design_investment_strategy(
            market_stats, client_profile, ths_industry_index
        )
        
        result = {
            'status': 'success',
            'design_date': datetime.now().isoformat(),
            'trust_structure': trust_type,
            'asset_plan': asset_plan,
            'distribution_scheme': distribution,
            'governance_structure': governance,
            'tax_planning': tax_planning,
            'investment_strategy': investment_strategy,
            'implementation_roadmap': self._generate_roadmap(),
            'data_source_info': self._get_data_source_info(),
            'ths_integration': {
                'industry_index': ths_industry_index,
                'company_financials': ths_financials,
                'derived_configs': ths_configs
            },
            'version': '4.0.0',
            'data_source_version': 'ths_api_v4'
        }
        
        # 添加数据质量标注
        data_quality_info = {}
        if market_stats and market_stats.quality_label:
            data_quality_info['market_data'] = {
                'source': market_stats.quality_label.source,
                'score': market_stats.quality_label.overall_score,
                'update_time': market_stats.quality_label.update_time,
                'freshness_score': market_stats.quality_label.freshness_score
            }
        
        if products and products[0].quality_label:
            data_quality_info['product_data'] = {
                'source': products[0].quality_label.source,
                'score': products[0].quality_label.overall_score,
                'product_count': len(products)
            }
        
        # 标注同花顺数据来源
        if ths_industry_index:
            data_quality_info['ths_industry_index'] = {
                'source': '同花顺iFinD',
                'index_code': ths_industry_index.get('code'),
                'index_name': ths_industry_index.get('index_name')
            }
        
        if ths_financials:
            data_quality_info['ths_company_financials'] = {
                'source': '同花顺iFinD',
                'companies_count': len(ths_financials)
            }
        
        if data_quality_info:
            result['data_quality'] = data_quality_info
        
        return result
    
    def _get_ths_industry_index(self) -> Optional[dict]:
        """
        获取同花顺信托行业指数
        
        整改内容：使用多元金融指数作为信托行业代理
        数据来源标注：同花顺iFinD
        """
        try:
            return self.data_provider.get_ths_industry_index()
        except Exception as e:
            logger.warning(f"获取同花顺行业指数失败: {e}")
            return None
    
    def _get_trust_companies_financials(self, companies: list) -> list:
        """
        获取信托公司财务数据
        
        整改内容：接入同花顺API获取ROE/净利润/营收等财务数据
        数据来源标注：同花顺iFinD
        """
        financials = []
        for company in companies:
            try:
                fin = self.data_provider.get_trust_company_financials(company)
                if fin:
                    financials.append({
                        'company': company,
                        'financials': fin,
                        'data_source': '同花顺iFinD'
                    })
            except Exception as e:
                logger.warning(f"获取{company}财务数据失败: {e}")
        return financials
    
    def _get_ths_derived_configs(self) -> list:
        """
        获取从同花顺数据派生的配置
        
        整改内容：对于无法API化的模板数据，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        try:
            return self.data_provider.get_ths_derived_configs('allocation') or []
        except Exception as e:
            logger.warning(f"获取同花顺派生配置失败: {e}")
            return []
    
    def _get_data_source_info(self) -> dict:
        """获取数据源信息"""
        info = self.data_provider.get_data_source_info()
        return {
            'last_used_adapter': info.get('last_used'),
            'available_adapters': [a['name'] for a in info.get('adapters', []) if a['available']],
            'timestamp': datetime.now().isoformat()
        }
    
    def _determine_trust_type(self, profile: dict, objectives: list) -> dict:
        """确定信托类型"""
        revocable = "资产隔离" in objectives or "asset_protection" in objectives
        
        residency = profile.get('residency', '中国')
        
        return {
            'type': '不可撤销家族信托' if revocable else '可撤销家族信托',
            'jurisdiction': '境内' if residency == '中国' else '离岸',
            'duration': '永续' if revocable else '委托人生命周期+21年',
            'reasoning': '基于资产隔离需求选择不可撤销结构' if revocable else '基于灵活性需求选择可撤销结构'
        }
    
    def _design_asset_plan(self, profile: dict, products: list, ths_industry_index: dict = None) -> dict:
        """设计资产注入方案（增强版，参考同花顺行业数据）"""
        total = profile.get('total_assets', 0)
        initial_ratio = 0.4
        initial_amount = total * initial_ratio
        
        # 分析市场产品类型分布
        asset_types = {}
        for p in products:
            inv_type = p.investment_type
            asset_types[inv_type] = asset_types.get(inv_type, 0) + 1
        
        # 基于同花顺行业指数调整配置策略
        market_sentiment = 'neutral'
        if ths_industry_index and ths_industry_index.get('change_pct'):
            change_pct = ths_industry_index.get('change_pct', 0)
            if change_pct > 2:
                market_sentiment = 'bullish'
            elif change_pct < -2:
                market_sentiment = 'bearish'
        
        # 按市场分布建议配置，考虑行业指数情绪
        suitable_assets = []
        if products:
            # 基于实际市场数据推荐
            for inv_type, count in sorted(asset_types.items(), key=lambda x: -x[1])[:3]:
                # 查找该类型的平均收益率
                type_products = [p for p in products if p.investment_type == inv_type]
                avg_yield = sum(p.expected_yield for p in type_products) / len(type_products) if type_products else 6.5
                
                weight = min(40, max(10, count * 10))
                
                # 根据行业指数情绪调整权重
                if market_sentiment == 'bullish' and '权益' in inv_type:
                    weight = min(50, weight + 10)  # 牛市增加权益配置
                elif market_sentiment == 'bearish' and '固收' in inv_type:
                    weight = min(50, weight + 10)  # 熊市增加固收配置
                
                suitable_assets.append({
                    'type': inv_type,
                    'percentage': weight,
                    'reason': f'市场主流配置（{count}个产品）',
                    'expected_yield': round(avg_yield, 2)
                })
        
        # 补充标准配置
        if not suitable_assets:
            suitable_assets = [
                {'type': '固定收益类信托', 'percentage': 40, 'reason': '市场主流配置，收益稳定', 'expected_yield': 6.5},
                {'type': '混合类信托', 'percentage': 30, 'reason': '平衡收益与风险', 'expected_yield': 7.5}
            ]
        
        # 添加现金和保单
        has_cash = any(a['type'] == '现金管理' for a in suitable_assets)
        if not has_cash:
            suitable_assets.append({'type': '现金及等价物', 'percentage': 15, 'reason': '流动性管理', 'expected_yield': 2.5})
        
        has_insurance = any('保单' in a['type'] or '保险' in a['type'] for a in suitable_assets)
        if not has_insurance:
            suitable_assets.append({'type': '保单', 'percentage': 15, 'reason': '杠杆效应与传承', 'expected_yield': 4.0})
        
        # 归一化权重
        total_weight = sum(a['percentage'] for a in suitable_assets)
        if total_weight != 100:
            for a in suitable_assets:
                a['percentage'] = round(a['percentage'] * 100 / total_weight)
        
        result = {
            'initial_funding': round(initial_amount, 2),
            'phased_injection': True,
            'suitable_assets': suitable_assets,
            'timeline': '建议分3年逐步完成资产注入',
            'market_reference': {
                'available_product_types': list(asset_types.keys()),
                'product_count': len(products),
                'data_freshness': '实时' if products and products[0].quality_label and products[0].quality_label.freshness_score > 70 else '缓存'
            }
        }
        
        # 添加同花顺行业指数参考
        if ths_industry_index:
            result['ths_industry_reference'] = {
                'index_name': ths_industry_index.get('index_name'),
                'index_code': ths_industry_index.get('code'),
                'change_pct': ths_industry_index.get('change_pct'),
                'market_sentiment': market_sentiment,
                'data_source': '同花顺iFinD'
            }
        
        return result
    
    def _design_distribution(self, profile: dict) -> dict:
        """设计分配方案"""
        children = profile.get('children', [])
        spouse = profile.get('spouse', True)
        
        scheme = {}
        
        if spouse:
            scheme['generation_1'] = {
                'beneficiaries': ['配偶'],
                'purpose': '生活保障',
                'amount': '每年固定生活费',
                'conditions': []
            }
        
        if children:
            scheme['generation_2'] = {
                'beneficiaries': [f'子女{i+1}' for i in range(children)],
                'purpose': '教育+创业+婚嫁',
                'amount': '按实际需求分配',
                'conditions': ['教育费用实报实销', '创业支持最高500万', '婚嫁支持200万']
            }
        
        scheme['generation_3'] = {
            'beneficiaries': ['孙辈（如适用）'],
            'purpose': '条件分配',
            'amount': '视信托资产状况',
            'conditions': ['大学毕业', '结婚', '生育']
        }
        
        return scheme
    
    def _design_governance(self, profile: dict) -> dict:
        """设计治理架构"""
        return {
            'trustee': {
                'type': '信托公司',
                'selection_criteria': ['托管规模', '家族信托经验', '投资能力'],
                'replacement_mechanism': '保护人可更换'
            },
            'protector': {
                'role': '委托人或其指定人士',
                'powers': [
                    '更换受托人',
                    '调整受益人范围',
                    '修改分配条件',
                    '终止信托（仅限可撤销信托）'
                ]
            },
            'investment_committee': {
                'members': ['委托人代表', '信托公司', '独立投资顾问'],
                'responsibilities': ['制定投资策略', '监督投资执行']
            },
            'advisory_board': {
                'optional': True,
                'members': ['家族成员', '法律顾问', '税务顾问']
            }
        }
    
    def _design_tax_planning(self, profile: dict, objectives: list) -> dict:
        """设计税务方案"""
        return {
            'current_tax_benefits': [
                '信托层面暂不征收所得税',
                '资产转移环节增值税优惠',
                '印花税减免'
            ],
            'distribution_tax': {
                'principle': '受益人取得分配时缴纳个人所得税',
                'rate': '按综合所得或偶然所得20%'
            },
            'considerations': [
                'CRS信息交换合规',
                '反避税条款适用',
                '建议咨询专业税务顾问'
            ]
        }
    
    def _design_investment_strategy(self, market_stats, profile: dict, ths_industry_index: dict = None) -> dict:
        """设计投资策略（增强版，参考同花顺行业数据）"""
        risk_profile = profile.get('risk_tolerance', '稳健型')
        
        # 基于风险画像的配置建议
        allocations = {
            '保守型': {'固定收益类': 70, '混合类': 20, '权益类': 10},
            '稳健型': {'固定收益类': 50, '混合类': 30, '权益类': 20},
            '平衡型': {'固定收益类': 40, '混合类': 35, '权益类': 25},
            '进取型': {'固定收益类': 30, '混合类': 35, '权益类': 35},
            '激进型': {'固定收益类': 20, '混合类': 30, '权益类': 50}
        }
        
        allocation = allocations.get(risk_profile, allocations['稳健型'])
        
        # 基于同花顺行业指数调整配置
        if ths_industry_index and ths_industry_index.get('change_pct'):
            change_pct = ths_industry_index.get('change_pct', 0)
            # 根据行业指数涨跌幅微调配置
            if change_pct > 3:
                # 行业强势，增加权益
                allocation['权益类'] = min(60, allocation['权益类'] + 5)
                allocation['固定收益类'] = max(10, allocation['固定收益类'] - 5)
            elif change_pct < -3:
                # 行业弱势，增加固收
                allocation['固定收益类'] = min(80, allocation['固定收益类'] + 5)
                allocation['权益类'] = max(5, allocation['权益类'] - 5)
        
        strategy = {
            'risk_profile': risk_profile,
            'allocation': allocation,
            'rebalancing_frequency': '季度',
            'investment_restrictions': [
                '单一产品不超过信托资产的20%',
                '非标债权合计不超过50%',
                '禁止投资限制性行业'
            ]
        }
        
        # 添加市场参考数据
        if market_stats:
            strategy['market_reference'] = {
                'current_avg_yield': market_stats.avg_yield,
                'yield_by_type': market_stats.yield_by_type,
                'data_source': market_stats.quality_label.source if market_stats.quality_label else None,
                'data_update_time': market_stats.quality_label.update_time if market_stats.quality_label else None
            }
        
        # 添加同花顺行业指数参考
        if ths_industry_index:
            strategy['ths_industry_reference'] = {
                'index_name': ths_industry_index.get('index_name'),
                'index_code': ths_industry_index.get('code'),
                'current_price': ths_industry_index.get('current_price'),
                'change_pct': ths_industry_index.get('change_pct'),
                'data_source': '同花顺iFinD'
            }
        
        return strategy
    
    def _generate_roadmap(self) -> list:
        """生成实施路线图"""
        return [
            {'phase': 1, 'duration': '1-2周', 'tasks': ['尽职调查', '方案细化', '信托文件起草']},
            {'phase': 2, 'duration': '2-4周', 'tasks': ['信托设立', '资产注入', '账户开立']},
            {'phase': 3, 'duration': '持续', 'tasks': ['投资管理', '定期报告', '分配执行']}
        ]


def main():
    parser = argparse.ArgumentParser(description='家族信托架构设计师 v4.0 - 同花顺API整改版')
    parser.add_argument('--profile', help='客户画像文件')
    parser.add_argument('--objectives', help='目标，逗号分隔')
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
    
    if args.profile:
        with open(args.profile, 'r') as f:
            profile = json.load(f)
    else:
        # 示例客户画像
        profile = {
            'name': '示例客户',
            'age': 55,
            'residency': '中国',
            'total_assets': 5000,
            'children': 2,
            'risk_tolerance': '稳健型'
        }
    
    objectives = args.objectives.split(',') if args.objectives else ['wealth_transfer', 'asset_protection']
    
    designer = FamilyTrustDesigner()
    result = designer.design(profile, objectives)
    
    print("=" * 60)
    print("🏛️ 家族信托架构设计方案")
    print("=" * 60)
    
    # 信托类型
    trust_type = result.get('trust_structure', {})
    print(f"\n📌 信托类型: {trust_type.get('type', 'N/A')}")
    print(f"   管辖地: {trust_type.get('jurisdiction', 'N/A')}")
    print(f"   期限: {trust_type.get('duration', 'N/A')}")
    
    # 资产方案
    asset_plan = result.get('asset_plan', {})
    print(f"\n💰 初始注资: {asset_plan.get('initial_funding', 'N/A')}万元")
    print(f"   资产配置:")
    for asset in asset_plan.get('suitable_assets', []):
        print(f"   - {asset['type']}: {asset['percentage']}% (预期收益: {asset.get('expected_yield', 'N/A')}%)")
    
    # 显示同花顺行业指数参考
    if asset_plan.get('ths_industry_reference'):
        ths_ref = asset_plan['ths_industry_reference']
        print(f"\n📈 同花顺行业指数参考:")
        print(f"   {ths_ref.get('index_name')} ({ths_ref.get('index_code')})")
        print(f"   涨跌幅: {ths_ref.get('change_pct')}%")
        print(f"   市场情绪: {ths_ref.get('market_sentiment')}")
        print(f"   数据来源: {ths_ref.get('data_source')}")
    
    # 投资策略
    strategy = result.get('investment_strategy', {})
    print(f"\n📊 投资策略: {strategy.get('risk_profile', 'N/A')}")
    if strategy.get('market_reference'):
        ref = strategy['market_reference']
        print(f"   市场参考收益率: {ref.get('current_avg_yield', 'N/A')}%")
    
    # 显示同花顺投资策略参考
    if strategy.get('ths_industry_reference'):
        ths_ref = strategy['ths_industry_reference']
        print(f"   同花顺行业指数: {ths_ref.get('index_name')}")
        print(f"   当前点位: {ths_ref.get('current_price')}")
        print(f"   涨跌幅: {ths_ref.get('change_pct')}%")
    
    # 数据源信息
    if 'data_source_info' in result:
        print(f"\n📡 数据源: {result['data_source_info'].get('last_used_adapter', 'N/A')}")
    
    if 'data_quality' in result:
        dq = result['data_quality']
        if 'market_data' in dq:
            print(f"   市场数据质量: {dq['market_data'].get('source', 'N/A')} (评分: {dq['market_data'].get('score', 0)})")
        if 'ths_industry_index' in dq:
            print(f"   同花顺行业指数: {dq['ths_industry_index'].get('source', 'N/A')}")
        if 'ths_company_financials' in dq:
            print(f"   同花顺公司财务: {dq['ths_company_financials'].get('source', 'N/A')} ({dq['ths_company_financials'].get('companies_count', 0)}家公司)")
    
    # 显示同花顺集成信息
    ths_integration = result.get('ths_integration', {})
    if ths_integration.get('company_financials'):
        print(f"\n🏢 信托公司财务数据 (同花顺iFinD):")
        for fin in ths_integration['company_financials'][:3]:
            company_fin = fin.get('financials', {})
            print(f"   - {fin.get('company')}: ROE {company_fin.get('roe', 'N/A')}%")
    
    print("\n" + "=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
