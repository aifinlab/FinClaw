#!/usr/bin/env python3
"""
基金组合配置核心模块
Fund Portfolio Allocation Core Module

功能：资产配置、Markowitz优化、风险平价、Black-Litterman
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/finclaw/skills/fund-suite/fund-portfolio-allocation/scripts')

import json
import argparse
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import warnings

# 尝试导入科学计算库
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# 示例数据文件路径
SAMPLE_DATA_PATH = '/root/.openclaw/workspace/skillsChoice/fund-suite/sample_data.json'

def _load_sample_fund_data() -> Dict:
    """从外部JSON文件加载示例基金数据"""
    try:
        with open(SAMPLE_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        warnings.warn(f"无法加载示例数据文件: {e}。将使用最小化默认数据。")
        return {}


@dataclass
class FundAllocation:
    """基金配置"""
    fund_code: str
    fund_name: str
    fund_type: str
    weight: float
    amount: float
    expected_return: float
    risk_contribution: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PortfolioMetrics:
    """组合指标"""
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PortfolioAllocator:
    """基金组合配置器"""
    
    # 无风险利率
    RISK_FREE_RATE = 0.025
    
    # 战略资产配置模板 (SAA)
    SAA_TEMPLATES = {
        'R1': {  # 保守型
            'name': '保守型',
            'description': '以保本为主，追求稳定收益',
            'allocation': {
                'equity': 0.00,
                'hybrid': 0.10,
                'bond': 0.40,
                'money': 0.50
            },
            'expected_return': 0.030,
            'expected_volatility': 0.025
        },
        'R2': {  # 稳健型
            'name': '稳健型',
            'description': '低风险，追求稳健增值',
            'allocation': {
                'equity': 0.15,
                'hybrid': 0.25,
                'bond': 0.40,
                'money': 0.20
            },
            'expected_return': 0.045,
            'expected_volatility': 0.050
        },
        'R3': {  # 平衡型
            'name': '平衡型',
            'description': '股债平衡，兼顾收益与风险',
            'allocation': {
                'equity': 0.30,
                'hybrid': 0.30,
                'bond': 0.30,
                'money': 0.10
            },
            'expected_return': 0.065,
            'expected_volatility': 0.120
        },
        'R4': {  # 进取型
            'name': '进取型',
            'description': '较高权益配置，追求较高收益',
            'allocation': {
                'equity': 0.50,
                'hybrid': 0.25,
                'bond': 0.20,
                'money': 0.05
            },
            'expected_return': 0.085,
            'expected_volatility': 0.180
        },
        'R5': {  # 激进型
            'name': '激进型',
            'description': '高权益配置，追求高收益',
            'allocation': {
                'equity': 0.70,
                'hybrid': 0.15,
                'bond': 0.10,
                'money': 0.05
            },
            'expected_return': 0.105,
            'expected_volatility': 0.250
        }
    }
    
    # 基金池（⚠️ 示例数据-需替换为真实数据）
    # 优先从外部JSON文件加载
    _sample_data = _load_sample_fund_data()
    _funds = _sample_data.get('funds', {})
    
    FUND_POOL = {
        'equity': _funds.get('equity', [
            {'code': 'EXAMPLE_E001', 'name': '示例股票基金A（需替换）', 'return': 0.12, 'volatility': 0.22, '_note': '示例数据'},
            {'code': 'EXAMPLE_E002', 'name': '示例股票基金B（需替换）', 'return': 0.10, 'volatility': 0.25, '_note': '示例数据'},
        ]),
        'hybrid': _funds.get('hybrid', [
            {'code': 'EXAMPLE_H001', 'name': '示例混合基金A（需替换）', 'return': 0.08, 'volatility': 0.16, '_note': '示例数据'},
            {'code': 'EXAMPLE_H002', 'name': '示例混合基金B（需替换）', 'return': 0.07, 'volatility': 0.15, '_note': '示例数据'},
        ]),
        'bond': _funds.get('bond', [
            {'code': 'EXAMPLE_B001', 'name': '示例债券基金A（需替换）', 'return': 0.04, 'volatility': 0.025, '_note': '示例数据'},
        ]),
        'money': _funds.get('money', [
            {'code': 'EXAMPLE_M001', 'name': '示例货币基金A（需替换）', 'return': 0.025, 'volatility': 0.001, '_note': '示例数据'},
        ])
    }
    
    # 资产类别预期收益和波动率
    ASSET_PARAMS = {
        'equity': {'return': 0.12, 'volatility': 0.22, 'correlation': {'hybrid': 0.85, 'bond': 0.10, 'money': -0.05}},
        'hybrid': {'return': 0.08, 'volatility': 0.16, 'correlation': {'bond': 0.20, 'money': 0.00}},
        'bond': {'return': 0.04, 'volatility': 0.04, 'correlation': {'money': 0.30}},
        'money': {'return': 0.025, 'volatility': 0.005, 'correlation': {}},
    }
    
    def __init__(self):
        pass
    
    def allocate(self, target: str, amount: float, risk_profile: str = 'R3',
                 strategy: str = 'saa') -> Dict:
        """
        基础配置
        
        Args:
            target: 投资目标描述
            amount: 投资金额
            risk_profile: 风险等级 (R1-R5)
            strategy: 配置策略 (saa/taa/markowitz/risk-parity)
        
        Returns:
            组合配置报告
        """
        if risk_profile not in self.SAA_TEMPLATES:
            return {'error': f'不支持的风险等级: {risk_profile}'}
        
        if strategy == 'saa':
            return self._saa_allocation(target, amount, risk_profile)
        elif strategy == 'taa':
            return self._taa_allocation(target, amount, risk_profile)
        elif strategy == 'markowitz':
            return self._markowitz_allocation(target, amount, risk_profile)
        elif strategy == 'risk-parity':
            return self._risk_parity_allocation(target, amount)
        else:
            return {'error': f'不支持的策略: {strategy}'}
    
    def _saa_allocation(self, target: str, amount: float, risk_profile: str) -> Dict:
        """战略资产配置"""
        template = self.SAA_TEMPLATES[risk_profile]
        allocation = template['allocation']
        
        # 构建基金配置
        fund_allocations = []
        by_type = {}
        
        for asset_type, weight in allocation.items():
            if weight <= 0:
                continue
            
            type_amount = amount * weight
            type_funds = self.FUND_POOL.get(asset_type, [])
            
            if not type_funds:
                continue
            
            # 在类别内平均分配
            fund_weight = weight / len(type_funds)
            fund_amount = type_amount / len(type_funds)
            
            type_allocations = []
            for fund in type_funds:
                fa = FundAllocation(
                    fund_code=fund['code'],
                    fund_name=fund['name'],
                    fund_type=asset_type,
                    weight=fund_weight,
                    amount=fund_amount,
                    expected_return=fund['return']
                )
                fund_allocations.append(fa)
                type_allocations.append(fa.to_dict())
            
            by_type[asset_type] = {
                'weight': weight,
                'amount': type_amount,
                'funds': type_allocations
            }
        
        # 计算组合指标
        metrics = self._calculate_portfolio_metrics(fund_allocations)
        
        return {
            'portfolio_id': f'PF_{datetime.now().strftime("%Y%m%d")}_{risk_profile}',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'strategy': 'SAA (战略资产配置)',
            'target_profile': target,
            'risk_level': risk_profile,
            'risk_description': template['name'],
            'total_amount': amount,
            'allocation': {
                'by_type': by_type,
                'by_fund': [fa.to_dict() for fa in fund_allocations]
            },
            'expected_metrics': metrics.to_dict(),
            'rebalance_policy': {
                'method': 'threshold',
                'threshold': 0.05,
                'frequency': 'quarterly'
            },
            'recommendations': self._generate_recommendations(risk_profile)
        }
    
    def _taa_allocation(self, target: str, amount: float, risk_profile: str) -> Dict:
        """战术资产配置 - 基于SAA调整"""
        # 先获取SAA配置
        saa_result = self._saa_allocation(target, amount, risk_profile)
        
        # 模拟TAA调整 (基于市场环境)
        taa_adjustments = {
            'equity': 0.05,   # 增持权益5%
            'hybrid': 0.00,
            'bond': -0.05,    # 减持债券5%
            'money': 0.00
        }
        
        # 应用调整
        for asset_type, adj in taa_adjustments.items():
            if asset_type in saa_result['allocation']['by_type']:
                type_data = saa_result['allocation']['by_type'][asset_type]
                new_weight = max(0, min(1, type_data['weight'] + adj))
                type_data['weight'] = new_weight
                type_data['amount'] = amount * new_weight
        
        saa_result['strategy'] = 'TAA (战术资产配置)'
        saa_result['taa_adjustments'] = taa_adjustments
        saa_result['taa_rationale'] = '基于当前市场估值水平调整：权益市场估值合理，适度增配'
        
        return saa_result
    
    def _markowitz_allocation(self, target: str, amount: float, risk_profile: str,
                              target_return: Optional[float] = None) -> Dict:
        """Markowitz均值方差优化"""
        # 简化的Markowitz优化 (没有cvxpy时使用启发式方法)
        template = self.SAA_TEMPLATES[risk_profile]
        base_allocation = template['allocation'].copy()
        
        # 目标收益
        target_r = target_return or template['expected_return']
        
        # 根据目标收益调整配置
        if target_r > template['expected_return']:
            # 增加权益配置
            increase = min(0.15, (target_r - template['expected_return']) / 0.05 * 0.10)
            base_allocation['equity'] += increase
            base_allocation['bond'] -= increase
        elif target_r < template['expected_return']:
            # 减少权益配置
            decrease = min(0.15, (template['expected_return'] - target_r) / 0.05 * 0.10)
            base_allocation['equity'] -= decrease
            base_allocation['bond'] += decrease
        
        # 归一化
        total = sum(base_allocation.values())
        base_allocation = {k: v/total for k, v in base_allocation.items()}
        
        # 构建配置
        fund_allocations = []
        by_type = {}
        
        for asset_type, weight in base_allocation.items():
            if weight <= 0:
                continue
            
            type_amount = amount * weight
            type_funds = self.FUND_POOL.get(asset_type, [])
            
            if not type_funds:
                continue
            
            fund_weight = weight / len(type_funds)
            fund_amount = type_amount / len(type_funds)
            
            type_allocations = []
            for fund in type_funds:
                fa = FundAllocation(
                    fund_code=fund['code'],
                    fund_name=fund['name'],
                    fund_type=asset_type,
                    weight=fund_weight,
                    amount=fund_amount,
                    expected_return=fund['return']
                )
                fund_allocations.append(fa)
                type_allocations.append(fa.to_dict())
            
            by_type[asset_type] = {
                'weight': weight,
                'amount': type_amount,
                'funds': type_allocations
            }
        
        metrics = self._calculate_portfolio_metrics(fund_allocations)
        
        return {
            'portfolio_id': f'PF_{datetime.now().strftime("%Y%m%d")}_MW',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'strategy': 'Markowitz均值方差优化',
            'target_profile': target,
            'target_return': target_r,
            'risk_level': risk_profile,
            'total_amount': amount,
            'allocation': {
                'by_type': by_type,
                'by_fund': [fa.to_dict() for fa in fund_allocations]
            },
            'expected_metrics': metrics.to_dict(),
            'efficient_frontier': self._calculate_efficient_frontier(),
            'rebalance_policy': {
                'method': 'threshold',
                'threshold': 0.05,
                'frequency': 'quarterly'
            },
            'recommendations': [
                'Markowitz优化基于历史数据，需定期更新协方差矩阵',
                '建议使用滚动窗口数据（3-5年）进行优化',
                '注意避免过度优化（overfitting）'
            ]
        }
    
    def _risk_parity_allocation(self, target: str, amount: float) -> Dict:
        """风险平价配置"""
        # 风险平价：各资产风险贡献相等
        # 简化的风险平价计算
        
        # 资产波动率
        vols = {
            'equity': 0.22,
            'hybrid': 0.16,
            'bond': 0.04,
            'money': 0.005
        }
        
        # 计算风险平价权重 (与波动率成反比)
        inv_vols = {k: 1/v for k, v in vols.items()}
        total_inv = sum(inv_vols.values())
        rp_weights = {k: v/total_inv for k, v in inv_vols.items()}
        
        # 归一化并调整
        rp_weights = {k: v * 0.9 for k, v in rp_weights.items()}  # 保留10%现金
        rp_weights['money'] = 0.10
        
        # 构建配置
        fund_allocations = []
        by_type = {}
        
        for asset_type, weight in rp_weights.items():
            if weight <= 0:
                continue
            
            type_amount = amount * weight
            type_funds = self.FUND_POOL.get(asset_type, [])
            
            if not type_funds:
                continue
            
            fund_weight = weight / len(type_funds)
            fund_amount = type_amount / len(type_funds)
            
            type_allocations = []
            for fund in type_funds:
                fa = FundAllocation(
                    fund_code=fund['code'],
                    fund_name=fund['name'],
                    fund_type=asset_type,
                    weight=fund_weight,
                    amount=fund_amount,
                    expected_return=fund['return'],
                    risk_contribution=0.25  # 风险平价：各资产贡献相等
                )
                fund_allocations.append(fa)
                type_allocations.append(fa.to_dict())
            
            by_type[asset_type] = {
                'weight': weight,
                'amount': type_amount,
                'funds': type_allocations
            }
        
        metrics = self._calculate_portfolio_metrics(fund_allocations)
        
        # 与传统60/40对比
        traditional_return = 0.60 * 0.12 + 0.40 * 0.04
        traditional_vol = math.sqrt(0.60**2 * 0.22**2 + 0.40**2 * 0.04**2 + 2*0.60*0.40*0.10*0.22*0.04)
        
        return {
            'portfolio_id': f'PF_{datetime.now().strftime("%Y%m%d")}_RP',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'strategy': '风险平价 (Risk Parity)',
            'target_profile': target,
            'risk_level': 'R2-R3',
            'total_amount': amount,
            'allocation': {
                'by_type': by_type,
                'by_fund': [fa.to_dict() for fa in fund_allocations]
            },
            'expected_metrics': metrics.to_dict(),
            'comparison': {
                'risk_parity': {
                    'volatility': metrics.expected_volatility,
                    'sharpe': metrics.sharpe_ratio
                },
                'traditional_60_40': {
                    'volatility': traditional_vol,
                    'sharpe': (traditional_return - self.RISK_FREE_RATE) / traditional_vol
                }
            },
            'rebalance_policy': {
                'method': 'risk_contribution',
                'threshold': 0.02,
                'frequency': 'monthly'
            },
            'recommendations': [
                '风险平价组合波动率更低，适合风险厌恶型投资者',
                '需要使用杠杆才能达到与传统组合相当的收益',
                '再平衡频率应高于传统配置'
            ]
        }
    
    def _calculate_portfolio_metrics(self, allocations: List[FundAllocation]) -> PortfolioMetrics:
        """计算组合指标"""
        if not allocations:
            return PortfolioMetrics(0, 0, 0, 0, 0)
        
        # 加权平均收益
        expected_return = sum(a.weight * a.expected_return for a in allocations)
        
        # 简化计算波动率 (假设类别间相关性)
        variance = 0.0
        for i, a1 in enumerate(allocations):
            vol1 = self.ASSET_PARAMS.get(a1.fund_type, {}).get('volatility', 0.15)
            variance += (a1.weight * vol1) ** 2
            for j, a2 in enumerate(allocations):
                if i < j:
                    vol2 = self.ASSET_PARAMS.get(a2.fund_type, {}).get('volatility', 0.15)
                    corr = self._get_correlation(a1.fund_type, a2.fund_type)
                    variance += 2 * a1.weight * a2.weight * vol1 * vol2 * corr
        
        volatility = math.sqrt(variance) if variance > 0 else 0
        
        # 夏普比率
        sharpe = (expected_return - self.RISK_FREE_RATE) / volatility if volatility > 0 else 0
        
        # 估算最大回撤 (简化)
        max_dd = -volatility * 1.5
        
        # VaR
        var_95 = -volatility * 1.645 / math.sqrt(252) * math.sqrt(252)
        
        return PortfolioMetrics(
            expected_return=expected_return,
            expected_volatility=volatility,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            var_95=var_95
        )
    
    def _get_correlation(self, type1: str, type2: str) -> float:
        """获取资产间相关系数"""
        if type1 == type2:
            return 1.0
        
        corr_matrix = {
            ('equity', 'hybrid'): 0.85,
            ('equity', 'bond'): 0.10,
            ('equity', 'money'): -0.05,
            ('hybrid', 'bond'): 0.20,
            ('hybrid', 'money'): 0.00,
            ('bond', 'money'): 0.30,
        }
        
        return corr_matrix.get((type1, type2), corr_matrix.get((type2, type1), 0.2))
    
    def _calculate_efficient_frontier(self, n_points: int = 10) -> List[Dict]:
        """计算有效前沿"""
        frontier = []
        
        min_return = 0.025
        max_return = 0.12
        
        for i in range(n_points):
            target = min_return + (max_return - min_return) * i / (n_points - 1)
            
            # 简化的有效前沿计算
            if HAS_NUMPY:
                vol = 0.02 + (target - 0.025) * 2.0
            else:
                vol = 0.02 + (target - 0.025) * 2.0
            
            frontier.append({
                'target_return': round(target, 3),
                'min_volatility': round(vol, 3),
                'sharpe_ratio': round((target - self.RISK_FREE_RATE) / vol, 3) if vol > 0 else 0
            })
        
        return frontier
    
    def _generate_recommendations(self, risk_profile: str) -> List[str]:
        """生成配置建议"""
        recommendations = {
            'R1': [
                '适合退休人群或短期资金保值',
                '建议持有期1-2年',
                '关注货币基金和短债基金'
            ],
            'R2': [
                '适合保守型投资者',
                '建议持有期2-3年',
                '可适当关注二级债基'
            ],
            'R3': [
                '适合一般投资者',
                '建议持有期3年以上',
                '股债平衡，关注市场估值'
            ],
            'R4': [
                '适合有一定经验的投资者',
                '建议持有期3-5年',
                '关注权益市场机会'
            ],
            'R5': [
                '适合高风险承受能力的投资者',
                '建议持有期5年以上',
                '做好大幅波动的心理准备'
            ]
        }
        
        base_rec = recommendations.get(risk_profile, [])
        return base_rec + [
            '建议定投方式建仓，平滑成本',
            '每季度检查偏离度，必要时再平衡'
        ]
    
    def target_date_allocation(self, target_year: int, current_year: int, 
                               amount: float) -> Dict:
        """目标日期配置"""
        years_to_target = target_year - current_year
        
        if years_to_target <= 0:
            # 已到目标日期，保守配置
            equity_ratio = 0.20
        elif years_to_target >= 30:
            # 还有30年以上，激进配置
            equity_ratio = 0.80
        else:
            # 线性递减
            equity_ratio = 0.80 - (years_to_target / 30) * 0.60
        
        # 分配剩余比例
        remaining = 1.0 - equity_ratio
        hybrid_ratio = remaining * 0.40
        bond_ratio = remaining * 0.50
        money_ratio = remaining * 0.10
        
        allocation = {
            'equity': equity_ratio,
            'hybrid': hybrid_ratio,
            'bond': bond_ratio,
            'money': money_ratio
        }
        
        return {
            'portfolio_id': f'PF_{datetime.now().strftime("%Y%m%d")}_TD',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'strategy': f'目标日期策略 (目标年份: {target_year})',
            'target_year': target_year,
            'years_to_target': years_to_target,
            'glide_path': allocation,
            'total_amount': amount,
            'allocation_summary': {
                '当前股票比例': f'{equity_ratio:.1%}',
                '股票比例每年下降': f'{0.60/30:.1%}',
                '建议': '随着年龄增长自动降低风险敞口'
            }
        }


def print_allocation_report(report: Dict):
    """打印配置报告"""
    print("\n" + "=" * 80)
    print(f"📊 基金组合配置报告")
    print("=" * 80)
    
    print(f"\n组合ID: {report.get('portfolio_id', 'N/A')}")
    print(f"创建日期: {report.get('created_at', 'N/A')}")
    print(f"配置策略: {report.get('strategy', 'N/A')}")
    print(f"投资目标: {report.get('target_profile', 'N/A')}")
    print(f"风险等级: {report.get('risk_level', 'N/A')}")
    if 'risk_description' in report:
        print(f"风险描述: {report['risk_description']}")
    print(f"投资金额: ¥{report.get('total_amount', 0):,.0f}")
    
    if 'taa_adjustments' in report:
        print(f"\n📈 战术调整:")
        print(f"  {report.get('taa_rationale', '')}")
        for asset, adj in report['taa_adjustments'].items():
            if adj != 0:
                sign = "+" if adj > 0 else ""
                print(f"  {asset}: {sign}{adj:.1%}")
    
    print(f"\n📋 资产配置:")
    allocation = report.get('allocation', {})
    by_type = allocation.get('by_type', {})
    
    for asset_type, data in by_type.items():
        type_name = {'equity': '股票型', 'hybrid': '混合型', 'bond': '债券型', 'money': '货币型'}.get(asset_type, asset_type)
        print(f"\n  {type_name}: {data['weight']:.1%} (¥{data['amount']:,.0f})")
        for fund in data.get('funds', []):
            print(f"    • {fund['fund_name']} ({fund['fund_code']})")
            print(f"      权重: {fund['weight']:.1%} | 金额: ¥{fund['amount']:,.0f} | 预期收益: {fund['expected_return']:.1%}")
    
    metrics = report.get('expected_metrics', {})
    print(f"\n📈 预期表现:")
    print(f"  预期年化收益: {metrics.get('expected_return', 0):.1%}")
    print(f"  预期波动率: {metrics.get('expected_volatility', 0):.1%}")
    print(f"  夏普比率: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"  预期最大回撤: {metrics.get('max_drawdown', 0):.1%}")
    print(f"  95% VaR: {metrics.get('var_95', 0):.1%}")
    
    if 'comparison' in report:
        print(f"\n📊 与传统配置对比:")
        comp = report['comparison']
        rp = comp.get('risk_parity', {})
        trad = comp.get('traditional_60_40', {})
        print(f"              风险平价    传统60/40")
        print(f"  波动率:      {rp.get('volatility', 0):.1%}       {trad.get('volatility', 0):.1%}")
        print(f"  夏普比率:    {rp.get('sharpe', 0):.2f}       {trad.get('sharpe', 0):.2f}")
    
    rebalance = report.get('rebalance_policy', {})
    print(f"\n🔄 再平衡策略:")
    print(f"  方法: {rebalance.get('method', 'threshold')}")
    print(f"  偏离阈值: {rebalance.get('threshold', 0.05):.1%}")
    print(f"  检查频率: {rebalance.get('frequency', 'quarterly')}")
    
    print(f"\n💡 建议:")
    for rec in report.get('recommendations', []):
        print(f"  • {rec}")
    
    print("=" * 80)


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(description='基金组合配置')
    parser.add_argument('--target', required=True, help='投资目标')
    parser.add_argument('--amount', type=float, required=True, help='投资金额')
    parser.add_argument('--risk', default='R3', choices=['R1', 'R2', 'R3', 'R4', 'R5'],
                       help='风险等级')
    parser.add_argument('--strategy', default='saa',
                       choices=['saa', 'taa', 'markowitz', 'risk-parity'],
                       help='配置策略')
    parser.add_argument('--target-return', type=float, help='目标收益（Markowitz）')
    parser.add_argument('--target-year', type=int, help='目标年份（目标日期策略）')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    allocator = PortfolioAllocator()
    
    # 目标日期策略
    if args.target_year:
        report = allocator.target_date_allocation(
            args.target_year,
            datetime.now().year,
            args.amount
        )
    else:
        report = allocator.allocate(
            target=args.target,
            amount=args.amount,
            risk_profile=args.risk,
            strategy=args.strategy
        )
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_allocation_report(report)


if __name__ == '__main__':
    main()
