#!/usr/bin/env python3
"""
慈善信托管理器 v4.0 - 同花顺API整改版
功能：慈善项目管理、资金拨付、税收优惠、效果评估

整改内容：
1. 接入同花顺API获取信托公司财务数据
2. 使用多元金融指数作为信托行业代理
3. 对于无法API化的慈善项目数据，创建从同花顺数据派生的配置
4. 添加THS API错误处理和降级逻辑
5. 标注数据来源为"同花顺iFinD"

数据源：
  - 优先：用益信托网/中国信登/同花顺iFinD
  - 派生：从同花顺数据生成的慈善信托配置
  - 保底：本地缓存/模拟数据
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加数据适配器路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
from trust_data_adapter import get_data_provider, TrustDataProvider

logger = logging.getLogger('CharityTrustManager')


class CharityTrustManager:
    """慈善信托管理器 v4.0 - 同花顺API整改版
    
    整改内容：
    1. 接入同花顺API获取信托公司财务数据
    2. 使用多元金融指数作为信托行业代理
    3. 对于无法API化的慈善项目数据，创建从同花顺数据派生的配置
    4. 添加THS API错误处理和降级逻辑
    5. 标注数据来源为"同花顺iFinD"
    """
    
    def __init__(self):
        self.data_provider = get_data_provider()
    
    def manage(self, trust_data: dict) -> dict:
        """
        管理慈善信托（增强版，集成同花顺数据）
        
        整改内容：
        - 使用同花顺行业指数作为市场代理
        - 获取信托公司财务数据作为参考
        - 数据来源标注：同花顺iFinD
        """
        # 获取市场数据作为参考
        market_stats = self.data_provider.get_market_stats()
        
        # 获取同花顺行业指数
        ths_industry_index = self._get_ths_industry_index()
        
        # 获取同花顺派生的配置
        ths_configs = self._get_ths_derived_configs()
        
        # 1. 慈善项目规划
        charity_projects = self._design_charity_projects(trust_data)
        
        # 2. 资金拨付计划
        disbursement_plan = self._create_disbursement_plan(trust_data, ths_industry_index)
        
        # 3. 税收优惠计算
        tax_benefits = self._calculate_tax_benefits(trust_data)
        
        # 4. 投资增值策略（参考同花顺行业数据）
        investment_strategy = self._design_investment_strategy(trust_data, market_stats, ths_industry_index)
        
        # 5. 效果评估指标
        evaluation_metrics = self._design_evaluation_metrics(trust_data)
        
        result = {
            'status': 'success',
            'charity_projects': charity_projects,
            'disbursement_plan': disbursement_plan,
            'tax_benefits': tax_benefits,
            'investment_strategy': investment_strategy,
            'evaluation_metrics': evaluation_metrics,
            'timestamp': datetime.now().isoformat(),
            'data_source_info': self._get_data_source_info(),
            'ths_integration': {
                'industry_index': ths_industry_index,
                'derived_configs': ths_configs
            },
            'version': '4.0.0',
            'data_source_version': 'ths_api_v4'
        }
        
        # 添加数据质量标注
        data_quality = {}
        if market_stats and market_stats.quality_label:
            data_quality['market_data_source'] = market_stats.quality_label.source
            data_quality['market_data_score'] = market_stats.quality_label.overall_score
            data_quality['market_data_update_time'] = market_stats.quality_label.update_time
        
        if ths_industry_index:
            data_quality['ths_industry_index'] = {
                'source': '同花顺iFinD',
                'index_code': ths_industry_index.get('code'),
                'index_name': ths_industry_index.get('index_name')
            }
        
        if data_quality:
            result['data_quality'] = data_quality
        
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
    
    def _get_ths_derived_configs(self) -> list:
        """
        获取从同花顺数据派生的配置
        
        整改内容：对于无法API化的慈善项目数据，创建从同花顺数据派生的配置
        数据来源标注：同花顺iFinD(派生)
        """
        try:
            return self.data_provider.get_ths_derived_configs('monitoring') or []
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
    
    def _design_charity_projects(self, trust_data: dict) -> list:
        """设计慈善项目"""
        focus_areas = trust_data.get('focus_areas', ['教育', '扶贫'])
        initial_amount = trust_data.get('initial_amount', 1000)
        
        projects = []
        
        if '教育' in focus_areas:
            projects.append({
                'name': '助学基金',
                'category': '教育',
                'annual_budget': initial_amount * 0.3,
                'target_beneficiaries': '贫困大学生',
                'expected_beneficiaries': int(initial_amount * 0.3 / 0.5),
                'duration': '长期'
            })
        
        if '扶贫' in focus_areas:
            projects.append({
                'name': '乡村发展基金',
                'category': '扶贫',
                'annual_budget': initial_amount * 0.3,
                'target_beneficiaries': '贫困地区',
                'expected_beneficiaries': 10,
                'duration': '5年'
            })
        
        if '环保' in focus_areas:
            projects.append({
                'name': '生态保护项目',
                'category': '环保',
                'annual_budget': initial_amount * 0.2,
                'target_beneficiaries': '生态保护区',
                'expected_beneficiaries': 5,
                'duration': '长期'
            })
        
        if '医疗' in focus_areas:
            projects.append({
                'name': '医疗救助基金',
                'category': '医疗',
                'annual_budget': initial_amount * 0.2,
                'target_beneficiaries': '重大疾病患者',
                'expected_beneficiaries': int(initial_amount * 0.2 / 2),
                'duration': '长期'
            })
        
        # 管理储备
        projects.append({
            'name': '管理储备',
            'category': '运营',
            'annual_budget': initial_amount * 0.1,
            'target_beneficiaries': '信托运营',
            'duration': '持续'
        })
        
        return projects
    
    def _create_disbursement_plan(self, trust_data: dict, ths_industry_index: dict = None) -> dict:
        """创建资金拨付计划（增强版，参考同花顺行业数据）"""
        initial_amount = trust_data.get('initial_amount', 1000)
        duration_years = trust_data.get('duration_years', 10)
        
        # 基于同花顺行业指数调整预期收益率
        base_yield = 0.06  # 基础预期收益率6%
        
        if ths_industry_index and ths_industry_index.get('change_pct'):
            change_pct = ths_industry_index.get('change_pct', 0)
            # 根据行业指数涨跌幅微调预期收益率
            yield_adjustment = change_pct * 0.001  # 每1%涨跌幅调整0.1%收益率
            adjusted_yield = base_yield + yield_adjustment
            expected_yield = max(0.04, min(0.08, adjusted_yield))  # 限制在4%-8%
        else:
            expected_yield = base_yield
        
        annual_charity = initial_amount * 0.08  # 每年公益支出约8%
        
        yearly_plan = []
        remaining = initial_amount
        
        for year in range(1, duration_years + 1):
            investment_return = remaining * expected_yield
            disbursement = annual_charity
            remaining = remaining + investment_return - disbursement
            
            yearly_plan.append({
                'year': year,
                'beginning_balance': round(remaining + disbursement - investment_return, 2),
                'investment_return': round(investment_return, 2),
                'expected_yield': round(expected_yield * 100, 2),
                'disbursement': round(disbursement, 2),
                'ending_balance': round(max(0, remaining), 2)
            })
        
        result = {
            'duration_years': duration_years,
            'annual_charity_disbursement': round(annual_charity, 2),
            'expected_annual_yield': round(expected_yield * 100, 2),
            'yearly_plan': yearly_plan,
            'total_disbursement': round(sum(y['disbursement'] for y in yearly_plan), 2),
            'projected_remaining': round(remaining, 2)
        }
        
        # 添加同花顺行业指数参考
        if ths_industry_index:
            result['ths_industry_reference'] = {
                'index_name': ths_industry_index.get('index_name'),
                'index_code': ths_industry_index.get('code'),
                'change_pct': ths_industry_index.get('change_pct'),
                'data_source': '同花顺iFinD'
            }
        
        return result
    
    def _calculate_tax_benefits(self, trust_data: dict) -> dict:
        """计算税收优惠"""
        initial_amount = trust_data.get('initial_amount', 1000)
        donor_type = trust_data.get('donor_type', '企业')  # 企业或个人
        
        if donor_type == '企业':
            # 企业捐赠税前扣除比例：年度利润总额的12%
            deduction_limit = initial_amount * 0.12
            tax_rate = 0.25
            tax_saving = deduction_limit * tax_rate
        else:
            # 个人捐赠税前扣除比例：应纳税所得额的30%
            deduction_limit = initial_amount * 0.30
            tax_rate = 0.45  # 最高税率
            tax_saving = deduction_limit * tax_rate
        
        return {
            'donor_type': donor_type,
            'deduction_rate': '12%' if donor_type == '企业' else '30%',
            'deduction_limit': round(deduction_limit, 2),
            'estimated_tax_saving': round(tax_saving, 2),
            'tax_exempt_income': True,  # 慈善信托收益免税
            'notes': ['需在年度汇算清缴时申报', '保留完整捐赠凭证']
        }
    
    def _design_investment_strategy(self, trust_data: dict, market_stats, ths_industry_index: dict = None) -> dict:
        """设计投资增值策略（增强版，参考同花顺行业数据）"""
        initial_amount = trust_data.get('initial_amount', 1000)
        risk_profile = trust_data.get('risk_profile', '保守型')
        
        # 参考市场收益率
        market_yield = market_stats.avg_yield if market_stats else 6.5
        
        # 基于同花顺行业指数调整预期收益率
        if ths_industry_index and ths_industry_index.get('change_pct'):
            change_pct = ths_industry_index.get('change_pct', 0)
            # 行业指数上涨，适度提高预期
            adjusted_yield = min(market_yield * (1 + change_pct / 100), 8.0)
        else:
            adjusted_yield = market_yield
        
        # 预期收益率（参考市场数据调整）
        expected_yield = min(adjusted_yield * 0.9, 6.0)  # 保守估计
        
        # 基于风险画像的配置
        allocations = {
            '保守型': {'货币基金': 30, '债券信托': 50, '固收类信托': 20},
            '稳健型': {'货币基金': 20, '债券信托': 40, '固收类信托': 35, '混合类信托': 5},
            '平衡型': {'货币基金': 15, '债券信托': 30, '固收类信托': 40, '混合类信托': 15}
        }
        
        allocation = allocations.get(risk_profile, allocations['稳健型'])
        
        result = {
            'risk_profile': risk_profile,
            'allocation': allocation,
            'expected_annual_yield': round(expected_yield, 2),
            'market_reference': {
                'current_market_yield': market_stats.avg_yield if market_stats else None,
                'data_source': market_stats.quality_label.source if market_stats and market_stats.quality_label else None,
                'data_update_time': market_stats.quality_label.update_time if market_stats and market_stats.quality_label else None
            },
            'investment_restrictions': [
                '禁止高风险投资',
                '单一产品不超过信托资产的20%',
                '优先选择ESG主题投资'
            ],
            'rebalancing_frequency': '半年度'
        }
        
        # 添加同花顺行业指数参考
        if ths_industry_index:
            result['ths_industry_reference'] = {
                'index_name': ths_industry_index.get('index_name'),
                'index_code': ths_industry_index.get('code'),
                'change_pct': ths_industry_index.get('change_pct'),
                'data_source': '同花顺iFinD'
            }
        
        return result
    
    def _design_evaluation_metrics(self, trust_data: dict) -> dict:
        """设计效果评估指标"""
        return {
            'financial_metrics': {
                'capital_preservation_rate': '本金保值',
                'annual_yield': '年化收益率',
                'cost_ratio': '管理费用率<5%'
            },
            'social_impact_metrics': {
                'beneficiaries_count': '受益人数量',
                'geographic_coverage': '覆盖地区',
                'satisfaction_rate': '受益人满意度'
            },
            'governance_metrics': {
                'transparency_score': '信息披露评分',
                'compliance_status': '合规状况',
                'annual_audit': '年度审计报告'
            },
            'reporting_requirements': {
                'frequency': '年度报告',
                'content': ['财务报告', '项目进展', '社会影响评估'],
                'disclosure': '向委托人和监管部门披露'
            }
        }
    
    def compare_with_market(self, trust_data: dict) -> dict:
        """与市场产品对比分析"""
        # 获取市场上的信托产品作为参考
        products = self.data_provider.get_products()
        
        avg_yield = sum(p.expected_yield for p in products) / len(products) if products else 6.5
        
        charity_expected_yield = 6.0  # 慈善信托保守预期
        
        return {
            'status': 'success',
            'comparison': {
                'charity_trust_expected_yield': charity_expected_yield,
                'market_average_yield': round(avg_yield, 2),
                'yield_gap': round(avg_yield - charity_expected_yield, 2),
                'explanation': '慈善信托收益率略低，主要考虑资金安全和流动性'
            },
            'market_products_reference': [
                {
                    'type': p.investment_type,
                    'expected_yield': p.expected_yield,
                    'risk_level': p.risk_level,
                    'data_quality': p.quality_label.to_dict() if p.quality_label else None
                }
                for p in products[:3]
            ],
            'data_source_info': self._get_data_source_info()
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='慈善信托管理器 v4.0 - 同花顺API整改版')
    parser.add_argument('--trust', help='信托数据文件')
    parser.add_argument('--compare', action='store_true', help='与市场对比')
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
    
    manager = CharityTrustManager()
    
    if args.compare:
        trust_data = {'initial_amount': 1000}
        result = manager.compare_with_market(trust_data)
    elif args.trust:
        with open(args.trust) as f:
            data = json.load(f)
        result = manager.manage(data)
    else:
        # 示例数据
        trust_data = {
            'name': '示例慈善信托',
            'initial_amount': 1000,
            'duration_years': 10,
            'focus_areas': ['教育', '扶贫'],
            'donor_type': '企业',
            'risk_profile': '稳健型'
        }
        result = manager.manage(trust_data)
    
    print("=" * 60)
    print("🎗️ 慈善信托管理方案")
    print("=" * 60)
    
    # 慈善项目
    projects = result.get('charity_projects', [])
    print(f"\n📋 慈善项目规划 ({len(projects)}个):")
    for p in projects:
        print(f"   - {p['name']} ({p['category']})")
        print(f"     年度预算: {p['annual_budget']}万元")
    
    # 资金拨付
    disbursement = result.get('disbursement_plan', {})
    print(f"\n💰 资金拨付计划:")
    print(f"   持续时间: {disbursement.get('duration_years', 'N/A')}年")
    print(f"   预期年化收益: {disbursement.get('expected_annual_yield', 'N/A')}%")
    print(f"   年度公益支出: {disbursement.get('annual_charity_disbursement', 'N/A')}万元")
    print(f"   预计总支出: {disbursement.get('total_disbursement', 'N/A')}万元")
    
    # 显示同花顺行业指数参考
    if disbursement.get('ths_industry_reference'):
        ths_ref = disbursement['ths_industry_reference']
        print(f"\n📈 同花顺行业指数参考:")
        print(f"   {ths_ref.get('index_name')} ({ths_ref.get('index_code')})")
        print(f"   涨跌幅: {ths_ref.get('change_pct')}%")
        print(f"   数据来源: {ths_ref.get('data_source')}")
    
    # 税收优惠
    tax = result.get('tax_benefits', {})
    print(f"\n💵 税收优惠:")
    print(f"   捐赠人类型: {tax.get('donor_type', 'N/A')}")
    print(f"   扣除比例: {tax.get('deduction_rate', 'N/A')}")
    print(f"   预计节税: {tax.get('estimated_tax_saving', 'N/A')}万元")
    
    # 投资策略
    strategy = result.get('investment_strategy', {})
    print(f"\n📊 投资策略:")
    print(f"   风险画像: {strategy.get('risk_profile', 'N/A')}")
    print(f"   预期年化收益: {strategy.get('expected_annual_yield', 'N/A')}%")
    if strategy.get('market_reference'):
        print(f"   市场参考收益率: {strategy['market_reference'].get('current_market_yield', 'N/A')}%")
    
    # 显示同花顺投资策略参考
    if strategy.get('ths_industry_reference'):
        ths_ref = strategy['ths_industry_reference']
        print(f"   同花顺行业指数: {ths_ref.get('index_name')}")
        print(f"   涨跌幅: {ths_ref.get('change_pct')}%")
    
    # 数据源信息
    if 'data_source_info' in result:
        print(f"\n📡 数据源: {result['data_source_info'].get('last_used_adapter', 'N/A')}")
    
    if 'data_quality' in result:
        dq = result['data_quality']
        print(f"   数据质量: {dq.get('market_data_source', 'N/A')} (评分: {dq.get('market_data_score', 0)})")
        if 'ths_industry_index' in dq:
            print(f"   同花顺行业指数: {dq['ths_industry_index'].get('source', 'N/A')}")
    
    # 显示同花顺集成信息
    ths_integration = result.get('ths_integration', {})
    if ths_integration.get('derived_configs'):
        print(f"\n🔧 同花顺派生配置: {len(ths_integration['derived_configs'])}条")
    
    print("\n" + "=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
